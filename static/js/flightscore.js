 $( function() {
    var availableAirports = [
      "SEA, Seattle WA",
      "SFO, San Francisco CA",
      "SJC, San Jose CA",
      "PDX, Portland OR",
      "LAX, Los Angeles CA",
      "SAN, San Diego CA",
      "ATL, Atlanta GA",
      "ORD, Chicago IL",
      "DFW, Dallas TX",
      "JFK, New York NY",
      "DEN, Denver CO",
      "LAS, Las Vegas NV",
      "CLT, Charlotte NC",
      "PHX, Phoenix AZ",
      "MIA, Miami FL",
      "MCO, Orlando FL",
      "IAH, Houston TX",
      "EWR, Newark NJ",
      "MSP, Minneapolis MN",
      "BOS, Boston MA",
      "DTW, Detroit MI",
      "PHL, Philadelphia PA",
      "LGA, New York NY",
      "FLL, Fort Lauderdale FL",
      "BWI, Baltimore MD",
      "DCA, Washington DC",
      "SLC, Salt Lake City UT",
      "MDW, Chicago IL",
      "HNL, Honolulu HI",
      "TPA, Tampa FL",
      "DAL, Dallas TX",
      "STL, St Louis MO",
      "AUS, Austin TX",
      "OAK, Oakland CA",
      "MSY, New Orleans LA",
      "MCI, Kansas City MO",
      "SNA, Santa Ana CA",
      "SMF, Sacramento CA",
      "SJU, San Juan PR",
      "SAT, San Antonio TX",
      "IND, Indianapolis IN",
      "CLE, Cleveland OH",
      "PIT, Pittsburgh PA",
      "CMH, Columbus OH",
      "OGG, Kahului HI"
    ];

    $( "#origin" ).autocomplete({
      source: availableAirports
    });
    $( "#destination" ).autocomplete({
      source: availableAirports
    });
  } );