import os
import csv
from nexarClient import NexarClient

mpns = []

# Reading the MPNs from the input file
with open("C:/Users/Zach.Gunter/Documents/GitHub/nexar-first-supply-query/python/csvDemo/input.csv", newline="") as inputFile:
    data = csv.reader(inputFile, delimiter=" ", quotechar="|")
    for row in data:
        mpns += row[0].split(",")

# GraphQL query
gqlQuery = '''
query csvDemo ($queries: [SupPartMatchQuery!]!) {
  supMultiMatch (
    currency: "USD",
    queries: $queries
  ){
    parts {
      mpn
      name
      sellers {
        company {
          id
          name
        }
        offers {
          inventoryLevel
          prices {
            quantity
            convertedPrice
            convertedCurrency
          }
        }
      }
    }
  }
}
'''

if __name__ == "__main__":
    # Replace with your actual clientId and clientSecret
    clientId = "ad0db8d1-6173-4f04-8856-8772c782d0aa"
    clientSecret = "HcBqkUPaQUBu4ZQbFsqdU9DB4S8VF0wCrINT"
    nexar = NexarClient(clientId, clientSecret)

    queries = [{"start": 0, "limit": 1, "mpn": mpn} for mpn in mpns]
    variables = {"queries": queries}
    results = nexar.get_query(gqlQuery, variables)

    if results:
        with open("output.csv", "w", newline="") as outputFile:
            writer = csv.writer(outputFile)
            writer.writerow(["Part Number", "Vendor 1", "Vendor 1 Unit Price", "Vendor 2", "Vendor 2 Unit Price", "Vendor 3", "Vendor 3 Unit Price"])

            for i, query in enumerate(results.get("supMultiMatch", [])):
                # Get the original MPN from the input file
                input_mpn = mpns[i].strip()

                # Find the part in the query results that matches the input MPN
                part = query.get("parts", [])[0]
                part_mpn = part.get("mpn")

                # Only process the part if the MPN matches the input
                if part_mpn != input_mpn:
                    print(f"Warning: Mismatch in MPNs. Expected {input_mpn}, but got {part_mpn}. Skipping.")
                    continue
                
                # Collect all vendors and their prices for quantity = 1
                vendor_prices = []
                for seller in part.get("sellers", []):
                    for offer in seller.get("offers", []):
                        for price in offer.get("prices", []):
                            if price.get("quantity") == 1:  # We only want prices for quantity = 1
                                vendor_prices.append({
                                    "vendor": seller.get("company").get("name"),
                                    "price": price.get("convertedPrice")
                                })
                
                # Sort vendors by price (ascending)
                vendor_prices = sorted(vendor_prices, key=lambda x: x["price"])

                # Ensure there are at least 3 vendors
                if len(vendor_prices) >= 3:
                    cheapest = vendor_prices[0]
                    median = vendor_prices[len(vendor_prices) // 2]
                    expensive = vendor_prices[-1]

                    # Write the data in the desired format
                    writer.writerow([
                        part_mpn,
                        cheapest["vendor"], cheapest["price"],
                        median["vendor"], median["price"],
                        expensive["vendor"], expensive["price"]
                    ])
