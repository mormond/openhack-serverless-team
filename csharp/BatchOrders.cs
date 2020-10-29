using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.DurableTask;
using Microsoft.Azure.WebJobs.Extensions.Http;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Text;
using Microsoft.Azure.Documents.Client;

namespace Company.Function
{
    public static class BatchOrders
    {
        [FunctionName("EnsureAllFiles")]
        public static async Task RunOrchestrator(
            [OrchestrationTrigger] IDurableOrchestrationContext context)
        {
            //var outputs = new List<string>();

            var newCustomerFilename = context.GetInput<string>();
            var expectedFiles = new List<string>() { "OrderHeaderDetails.csv", "OrderLineItems.csv", "ProductInformation.csv" };
            var filesStillWaitingFor = new HashSet<string>(expectedFiles);

            while (filesStillWaitingFor.Any())
            {
                filesStillWaitingFor.Remove(newCustomerFilename.Substring(newCustomerFilename.LastIndexOf('-') + 1));
                if (filesStillWaitingFor.Count == 0)
                {
                    break;
                }

                newCustomerFilename = await context.WaitForExternalEvent<string>(@"newfile");
            }

            await context.CallActivityAsync(@"ConsolidateFiles", context.InstanceId);
        }

        [FunctionName("ConsolidateFiles")]
        public static async Task<bool> ConsolidateFiles(
            [ActivityTrigger] string orderId, 
            ILogger log)
        {
            log.LogInformation($"Consolidate files on OrderID: {orderId}");

            HttpClient client = new HttpClient();
            HttpRequestMessage request = new HttpRequestMessage(
                HttpMethod.Post,
                @"https://serverlessohmanagementapi.trafficmanager.net/api/order/combineOrderContent");

            request.Content = new StringContent("{ " +
                $"\"orderHeaderDetailsCSVUrl\": \"https://challenge6.blob.core.windows.net/orders/{orderId}-OrderHeaderDetails.csv\"," +
                $"\"orderLineItemsCSVUrl\": \"https://challenge6.blob.core.windows.net/orders/{orderId}-OrderLineItems.csv\"," +
                $"\"productInformationCSVUrl\": \"https://challenge6.blob.core.windows.net/orders/{orderId}-ProductInformation.csv\"" +
                " }", Encoding.UTF8, "application/json");

            //Read Server Response
            HttpResponseMessage response = await client.SendAsync(request);
            string consolidatedOrder = await response.Content.ReadAsStringAsync();

            log.LogInformation($"Calling SaveOrderAsync on string: >>>{consolidatedOrder}<<<");

            await SaveOrderAsync(consolidatedOrder);

            return true;
        }

        public static async Task SaveOrderAsync(string orderToSave)
        {

            Uri collectionUri = UriFactory.CreateDocumentCollectionUri("demodb", "orders");

            JToken token = JToken.Parse(orderToSave);

            using DocumentClient client = new DocumentClient(
                new Uri(@"https://meoserverlessdb.documents.azure.com:443/"),
                "Wjp3nRq5sa0Ddj9Q1Qfcu1IfJReRuW8Uy7z5cZL9xleFE02PKdXpREaS6cRu11wDukE5xRHEvYgyjBE5PbeRdA==");
            {
                foreach (var order in token)
                {
                    await client.CreateDocumentAsync(collectionUri, order);
                }
            }

            //log.LogInformation($"C# Queue trigger function inserted one row");
            //log.LogInformation($"Description={queueMessage}");
        }

        [FunctionName("BatchOrders_HttpStart")]
        public static async Task<HttpResponseMessage> HttpStart(
            [HttpTrigger(AuthorizationLevel.Anonymous, "get", "post")] HttpRequestMessage req,
            [DurableClient] IDurableOrchestrationClient starter,
            ILogger log)
        {

            var payloadFromEventGrid = JToken.ReadFrom(new JsonTextReader(new StreamReader(await req.Content.ReadAsStreamAsync())));
            dynamic eventGridSoleItem = (payloadFromEventGrid as JArray)?.SingleOrDefault();
            if (eventGridSoleItem == null)
            {
                return req.CreateErrorResponse(HttpStatusCode.BadRequest, $@"Expecting only one item in the Event Grid message");
            }

            if (eventGridSoleItem.eventType == @"Microsoft.EventGrid.SubscriptionValidationEvent")
            {
                //log.Verbose(@"Event Grid Validation event received.");
                return new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent($"{{ \"validationResponse\" : \"{((dynamic)payloadFromEventGrid)[0].data.validationCode}\" }}")
                };
            }

            string filename = ParseEventGridPayload(eventGridSoleItem, log);
            string orderid = filename.Substring(0, filename.IndexOf('-'));

            if (string.IsNullOrEmpty(filename))
            {   // The request either wasn't valid (filename couldn't be parsed) or not applicable (put in to a folder other than /inbound)
                return new HttpResponseMessage(HttpStatusCode.NoContent); //req.CreateCompatibleResponse(HttpStatusCode.NoContent);
            }

            var instanceForPrefix = await starter.GetStatusAsync(orderid);

            if (instanceForPrefix == null)
            {
                //starter.Log(log, $@"New instance needed for prefix '{orderid}'. Starting...");
                var retval = await starter.StartNewAsync(@"EnsureAllFiles", orderid, filename);
                //starter.Log(log, $@"Started. {retval}");
            
                log.LogDebug($"No existing instance. Starting new instance for {orderid}");

            }
            else
            {
                //starter.Log(log, $@"Instance already waiting. Current status: {instanceForPrefix.RuntimeStatus}. Firing 'newfile' event...");

                // if (instanceForPrefix.RuntimeStatus != OrchestrationRuntimeStatus.Running)
                // {
                //     if (instanceForPrefix.RuntimeStatus != OrchestrationRuntimeStatus.Terminated)
                //     {
                //         await starter.TerminateAsync(orderid, @"bounce");
                //     }
                //     var retval = await starter.StartNewAsync(@"EnsureAllFiles", orderid, filename);
                //     //starter.Log(log, $@"Restarted listener for {orderid}. {retval}");
                // }
                // else
                // {
                    log.LogDebug($"Found existing instance for {orderid}.");
                    log.LogDebug($"Current state is {instanceForPrefix.RuntimeStatus.ToString()}");
                    await starter.RaiseEventAsync(orderid, @"newfile", filename);
                // }
            }


            return starter.CreateCheckStatusResponse(req, orderid);

        }

        public static string ParseEventGridPayload(dynamic eventGridItem, ILogger log)
        {
            string filename = "";

            if (eventGridItem.eventType == @"Microsoft.Storage.BlobCreated"
                && eventGridItem.data.api == @"PutBlob")
            {
                try
                {
                    //Extract filename
                    var subject = (string)eventGridItem.subject;
                    filename = subject.Substring(subject.LastIndexOf('/') + 1);
                }
                catch (Exception ex)
                {
                    log.LogError(@"Error parsing Event Grid payload", ex);
                }
            }

            return filename;
        }
    }
}
