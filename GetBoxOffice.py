import pandas as pd
import numpy as np
from boxoffice_api import BoxOffice 

from datetime import date, timedelta

def getMovieBoxOfficeResult():
    
    start_date = date(2024, 5, 17)
    end_date = date.today() - timedelta(days=2)

    delta = timedelta(days=1)

    current_date = start_date
    date_list = []

    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += delta


    box_office = BoxOffice(outputformat="DF")
    # daily_data = box_office.get_daily("2024-07-17") 

    voteData = pd.read_csv("MovieAuction.csv")
    voteData = voteData.dropna(subset=['Movie'])
    voteData = voteData.iloc[:,0:7]
    voteData = voteData.fillna(0)
    # print(voteData)

    TotalBoxOffice = pd.DataFrame(columns = ['TD', 'YD', 'Release', 'Daily', '%± YD', '%± LW', 'Theaters', 'Avg',
        'To Date', 'Days', 'Distributor', "Date"])

    for dates in date_list:
        try:
            DayTotalBoxOffice = box_office.get_daily(dates)
            DayTotalBoxOffice['Date'] = dates
            TotalBoxOffice = pd.concat([TotalBoxOffice, DayTotalBoxOffice], axis = 0)
        except:
            print("Whoops")
    # TotalBoxOffice.to_csv("TempEditing.csv")

    # TotalBoxOffice = pd.read_csv('TempEditing.csv')

    voteData.columns = ['Release', 'Date', 'Andrew', 'Nick', 'Eric', 'Geoff',
        'Gavin']
    SummerMovies = voteData['Release'].to_numpy()
    SummerMovies = np.char.strip(SummerMovies.astype(str))
    BoxOfficeFiltered = TotalBoxOffice[TotalBoxOffice['Release'].isin(SummerMovies)]

    voteData['Owner'] = voteData.iloc[:,2:].idxmax(axis = 1)
    voteData['Price'] = voteData[['Andrew', 'Nick', 'Eric', 'Geoff', 'Gavin']].sum(axis=1)
    voteData = voteData[['Release', 'Owner', 'Price']]

    TotalVote = pd.merge(BoxOfficeFiltered, voteData, on='Release', how = 'left')
    TotalVote = TotalVote[['Daily', 'Release', 'Date', 'Owner', 'Price']]
    TotalVote['Daily'] = TotalVote['Daily'].str.replace(r'\D', '', regex=True).astype(float)
    print(TotalVote.columns)
    GeoffLeftover = pd.DataFrame([np.array([4, "Leftover Points", "2024-05-16", "Geoff", 0])], columns = TotalVote.columns)
    EricLeftover = pd.DataFrame([np.array([9, "Leftover Points", "2024-05-16", "Eric", 0])], columns = TotalVote.columns)
    GavinLeftover = pd.DataFrame([np.array([15, "Leftover Points", "2024-05-16", "Gavin", 0])], columns = TotalVote.columns)
    TotalVote = pd.concat([TotalVote, GeoffLeftover,EricLeftover,GavinLeftover])

    return TotalVote

df = getMovieBoxOfficeResult()

print(df)