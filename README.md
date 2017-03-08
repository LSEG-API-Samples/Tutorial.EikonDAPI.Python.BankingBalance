# Eikon Scripting Proxy Tutorial

In this tutorial, we will take a brief look at how to install Eikon Scripting Proxy and use it to get market data using python. A simple python script will replicate some of the functionality in the Thomson Reuters "Company Tearsheet" Excel template. The step by step walk through will look at main API call and how to extract different data points.

### This tutorial has following steps:
1. Install Eikon Scripting Proxy
2. Create an APP ID
3. Install Eikon API for Python
4. Writing first Eikon application
   + Initialize Eikon object
   + Retrieve data API call
   + Using data item browser
5. Gluing it all together

### Step 1: Install Eikon Scripting Proxy
Eikon Scripting Proxy is available for Windows/Linux and Mac OS. Proceed to [Download](link to proxy download) section in Developers portal and select the package applicable for your platform. You will need a valid Eikon user ID and password to run it. The scripting proxy connects to Thomson Reuters Eikon servers and starts listening on 36036 for local websocket connections. If proxy fails to start for some reason, the logs are stored at:

```
%AppData%\Thomson Reuters\Eikon Scripting Proxy for Windows   
~/.config/Eikon Scripting Proxy for Linux and Mac OS X
```

### Step 2: Create an APP ID
Every application using proxy must have a valid application ID. An App ID allows Thomson Reuters to keep track of application's data use, and enforce data limits and throttle any offending application. From within Eikon Scripting Proxy window, Click on button "Get an APP ID" to generate an application ID.


### Step 3: Install Eikon API
The Thomson Reuters python libraries conveniently wrap the raw message transcription between proxy and python and provide an easy to use data calls. The data output from python API is available as [Pandas Dataframe](link) or as JSON objects. To install Eikon package, open Python terminal and issue following command:

```
pip install eikon
```

### Step 4: Writing first Eikon application
Initialize the Eikon object

```
import eikon as ek   
ek.set_app_id("app_id_generated_in_previous_step")
```

The main data call we will use is get_data. The method signature is get_data(list of instruments, list of fields, options dictionary), where instrument is any valid RIC. If only one instrument or field is requested, then a string can be substituted instead of a list. Fields is any valid data field like BID, ASK etc applicable to requested instrument. For a list of all valid fields, click on "Data Item Browser" in the Scripting Proxy window. The Data Item Browser will show all available fields for every asset class. To narrow this list to applicable fields only, type in requested instrument in the search bar. The fields list can also be filtered by typing in keyword in search bar.

Some examples of get_data call are:

```
ek.get_data("IBM", "BID")	# get bid price of IBM   
ek.get_data("IBM", ["TR.PriceMainSector", "TR.TtlCmnSharesOut(Period=FY0)", "TR.RevenuePrimary(Period=FY0)"])   
ek.get_data(["GE", "IBM"], ["BID", "ASK"])   
ek.get_data("IBM", "TR.BIDPriceClose", {"curn": "GBP"})		# get closing bid price of IBM in Pound sterling   
```

Unless output="raw" is specified as one of the parameter in the get_data call, the returned data is a tuple containing response data and or error. The data from tuple can be extracted as:

```
data, error = ek.get_data("GE", ["BID", "ASK"])
```

where 
	error list contains reason if data request cannot be fulfilled. It is empty/null otherwise.   
	data is of type pandas DataFrame object. [Pandas DataFrame](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html)   
	DataFrame object is a two dimensional array type object, where columns represent requested fields and rows represent requested instruments.   
	For the call:   
		```
		data, error = ek.get_data(["GE", "IBM"], ["BID", "ASK"])   
		data would contain:   
			  Instrument     BID     ASK   
			0         GE   29.83   29.84   
			1        IBM  179.86  179.89   
		```
		Instrument is always the first item in column, followed by list of request fields

		
### Step 5: Complete Sample
Please refer to accompanying python "Company Tearsheet" sample. 

```
try:
	# get the primary RIC associated with this equity stock
	pRICDF, err = ek.get_data(ric, "TR.PrimaryQuote")
	pRIC = pRICDF.loc[0]["Primary Quote RIC"]

	# request general information
	giList1 = ["TR.CommonName()", "TR.HeadquartersCountry", "TR.ExchangeName", "TR.TRBCIndustryGroup", "TR.GICSSector", "TR.CompanyMarketCap.Currency"]
	ciFields, err = ek.get_data(pRIC, giList1)
	
	# get listed currency
	currency = ciFields.loc[0]["Currency"]
	
	# request more general information in destination currency
	giList2 = ["TR.PriceClose", "TR.Price52WeekHigh", "TR.PricePctChg52WkHigh", "TR.Price52WeekLow", "TR.PricePctChg52WkLow", "TR.PriceTargetMedian", "TR.PriceTargetMedian/TR.PriceClose-1"]
	fdOptions2 = {"curn": currency, "transpose": "y"}
	fdFields1, err = ek.get_data(pRIC, giList2, fdOptions2)

	giList3 = ["TR.PriceMainIndex", "TR.BetaFiveYear", "TR.DividendYield", "TR.SharesOutstanding", "TR.FreeFloat", "TR.FreeFloatPct()", "TR.CompanyMarketCap", "TR.EV"]
	fdOptions3 = {"scale": 6, "curn": currency, "transpose": "y"}
	fdFields2, err = ek.get_data(pRIC, giList3, fdOptions3)
	
	# request analysts
	aList = ["TR.RecLabel()", "TR.RecMean", "TR.NumOfRecommendations()", "TR.NumEstRevisingUp(WP=30d)", "TR.NumEstRevisingDown(WP=30d)"]
	aFields, err = ek.get_data(pRIC, aList)

	print("Company Tearsheet: %s" % ciFields.iat[0, 1]);
	print("General Information (Currency: %s)" % currency);
	print("Price (Previous Close):\t%.2f" % fdFields1.iat[0, 1]);
	
except (Exception, ValueError) as excp:
	print("Unable to get data for: %s. Is it a valid Equity RIC?" % ric)
	print("Exception message: %s" % excp)
```