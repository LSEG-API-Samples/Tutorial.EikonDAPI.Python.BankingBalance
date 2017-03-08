import sys
import eikon as ek

ek.set_app_id("your_eikon_id")

ric = input("Enter RIC (e.g. IBM, TD.TO): ")


def drawRange(num):
	tNum = (5 - num) * 6.25
	print("\t\t     ", end="")
	for i in range(int(tNum) - 1):
		print(" ", end="")
	print(u"▼", end="")
	print("")
	print("\t\t     ", end="")
	print(u"┌────┬────┬────┬────┬────┐")
	print("\t\tSell ", end="")
	print(u"│    │░░░░│▒▒▒▒│▓▓▓▓│████│", end="")
	print(" Buy")
	print("\t\t     ", end="")
	print(u"└────┴────┴────┴────┴────┘")


try:
	# check if it is a valid equity stock
	
	print("Getting primary RIC")
	# get the primary RIC associated with this equity stock
	pRICDF, err = ek.get_data(ric, "TR.PrimaryQuote")
	pRIC = pRICDF.loc[0]["Primary Quote RIC"]

	print("Requesting general information...", end="")
	sys.stdout.flush()
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
	print("done")

	print("Requesting analysts consensus...", end="")
	sys.stdout.flush()
	# request analysts
	aList = ["TR.RecLabel()", "TR.RecMean", "TR.NumOfRecommendations()", "TR.NumEstRevisingUp(WP=30d)", "TR.NumEstRevisingDown(WP=30d)"]
	aFields, err = ek.get_data(pRIC, aList)
	print("done")
	
	# display the sheet
	print("");
	print("");
	print(u"─────────────────────────────────────────────")
	print("Company Tearsheet: %s" % ciFields.iat[0, 1]);
	print(u"─────────────────────────────────────────────")
	
	print("Country:\t\t%s" % ciFields.iat[0, 2]);
	print("Exchange:\t\t%s" % ciFields.iat[0, 3]);
	print("Industry:\t\t%s" % ciFields.iat[0, 4]);
	print("Sector:\t\t\t%s" % ciFields.iat[0, 5]);
	print("Market Cap Currency:\t%s" % ciFields.iat[0, 6]);
	
	print("");
	print("");
	print("General Information (Currency: %s)" % currency);
	print(u"──────────────────────────────────")
	print("Price (Previous Close):\t%.2f" % fdFields1.iat[0, 1], end="");
	print("\tBeta 5 Year: (%s):\t%.2f" % (fdFields2.iat[0, 1], fdFields2.iat[0, 2]));
	print("Price - 52 Week High:\t%.2f" % fdFields1.iat[0, 2], end="");
	print("\tDividend Yield (Indicated):\t%.1f%%" % fdFields2.iat[0, 3]);
	print("Price - %% Below High:\t%.1f%%" % fdFields1.iat[0, 3], end="");
	print("\tShares Outstanding (MIL):\t%.0f" % fdFields2.iat[0, 4]);
	print("Price - 52 Week Low:\t%.2f" % fdFields1.iat[0, 4], end="");
	print("\tFloat Shares (MIL):\t\t%.0f" % fdFields2.iat[0, 5]);
	print("Price - %% Above Low:\t%.1f%%" % fdFields1.iat[0, 5], end="");
	print("\tFloat %% of O/S:\t\t\t%.1f%%" % fdFields2.iat[0, 6]);
	print("Median Price Target:\t%.2f" % fdFields1.iat[0, 6], end="");
	print("\tMarket Capitalization (MIL):\t%.0f" % fdFields2.iat[0, 7]);
	print("Implied Profit:\t\t%.1f%%" % fdFields1.iat[0, 7], end="");
	print("\tEnterprise Value (MIL):\t\t%.0f" % fdFields2.iat[0, 8]);

	print("");
	print("");
	print("Consensus Recommendation");
	print(u"────────────────────────")
	print("Recommendation:\t\t\t%s" % aFields.iat[0, 1]);
	# draw the range plot
	drawRange(aFields.iat[0, 2])	
	print("");
	print("# of Analysts:\t\t\t%s" % aFields.iat[0, 3]);
	print("Upgrades Last 30 Days:\t\t%s" % aFields.iat[0, 4]);
	print("Downgrades Last 30 Days:\t%s" % aFields.iat[0, 5]);
	print("");
	
	print("");
	print("");
	print("");

	
except (Exception, ValueError) as excp:
	print("Unable to get data for: %s. Is it a valid Equity RIC?" % ric)
	print("Exception message: %s" % excp)

