from shiny import App, Inputs, Outputs, Session, render, ui
from shinywidgets import output_widget, render_widget  
import plotly.express as px
import pandas as pd
from GetBoxOffice import getMovieBoxOfficeResult
from faicons import icon_svg
import os
app_ui = ui.page_fluid(
    ui.panel_title("Regulation Summer Movie Auction Results"),
    ui.navset_pill_list(
        ui.nav_panel("Podium", output_widget("BarPlot")),
        ui.nav_panel("Summer Daily Performance", output_widget("LinePlot")),
        ui.nav_panel("Cost Performance",output_widget("ReleaseCostEval") ),
        ui.nav_panel("About Me", ui.output_image("image" ),"Hi, My name is Matthew Wilcox. I am Graduate Data Science Student. Been just a Regulation Listener but this may make me a Comment leaver now I guess? I hope you enjoy this little project. If you want to check out any other projects I have done check out my Github or Linkedin!")    ),
    ui.input_action_button("Github", "Github",icon = icon_svg('github'), onclick ="window.open('https://github.com/MatthewLeeWilcox', '_blank')"),
    ui.input_action_button("LinkedIn", "LinkedIn", icon = icon_svg('linkedin'),onclick ="window.open('https://www.linkedin.com/in/matthewleewilcox/', '_blank')"),
    ui.input_action_button("Twitter", "Twitter", icon = icon_svg('twitter'),onclick ="window.open('https://x.com/WilcoxGKAcademy', '_blank')"),


)
from datetime import datetime
today = str(datetime.today().strftime("%Y %m %d")).replace(" ", "") + ".csv"

# if os.path.isfile(today) == True:
# movies = pd.read_csv(today)
# else:
movies = getMovieBoxOfficeResult()
#     movies.to_csv(today)
movies['Daily'] = movies['Daily'].astype(float)


moviesCumSum = movies.groupby(['Date', 'Owner'], as_index=False)['Daily'].sum()


moviesCumSum['Date'] = pd.to_datetime(moviesCumSum['Date'])
# print(df)
moviesCumSum = moviesCumSum.sort_values(by='Date')
date_range = pd.date_range(moviesCumSum['Date'].min(), moviesCumSum['Date'].max())
owner_range = moviesCumSum['Owner'].unique()
index = pd.MultiIndex.from_product([date_range, owner_range], names=['Date', 'Owner'])
moviesCumSum_filled = moviesCumSum.set_index(['Date', 'Owner']).reindex(index, fill_value=0).reset_index()
moviesCumSum_pivot = moviesCumSum_filled.pivot(index='Date', columns='Owner', values='Daily').reset_index()
moviesCumSum = moviesCumSum_pivot.melt(id_vars='Date', var_name='Owner', value_name='Daily')
moviesCumSum['Daily'] = pd.to_numeric(moviesCumSum['Daily'], errors='coerce')
# # df2 = df.groupby(['Date', 'Owner'], as_index = False)['Daily'].cumsum()
moviesCumSum['Cumulative_Total'] = moviesCumSum.groupby(['Owner'])['Daily'].transform('cumsum')

category_order = ['Andrew', 'Nick', 'Eric', 'Geoff', 'Gavin']


color_discrete_map = {'Andrew': 'blue', 'Nick': 'green', 'Eric': 'yellow', 'Geoff': 'red', 'Gavin': 'purple'}

def server(input,output,session):
    @render.data_frame
    def initial_df():
        return movies
    @render.data_frame
    def MovieTotalSum():
        tempMovieGroupDf = movies.groupby(['Release', 'Owner'], as_index=False)['Daily'].sum().sort_values(by = 'Daily', ascending=False)
        print(tempMovieGroupDf.sort_values(by = 'Daily'))
        tempMovieGroupDf['Daily'] = tempMovieGroupDf['Daily'].map('${:,.2f}'.format)
        return  render.DataTable(tempMovieGroupDf)
    @render.data_frame  
    def TableOutput():
        return render.DataTable(moviesCumSum)
    @render_widget
    def LinePlot():
        tempdf = moviesCumSum.copy()
        tempdf = tempdf.rename(columns= {'Cumulative_Total':"Total Box Office"})
        fig = px.line(tempdf, x = 'Date', y ='Total Box Office', color = 'Owner',color_discrete_map=color_discrete_map).update_layout(
            yaxis_title = "Total Domestic Box Office ($)", title = "Total Box Office ANEGG Performance", hovermode = "x"
        ).update_traces(mode="markers+lines", hovertemplate=None).update_xaxes(tickangle=45)
        return fig
    @render_widget
    def BarPlot():
        tempdf = movies.copy()
        tempdf = tempdf.groupby([ 'Owner'], as_index=False)['Daily'].sum()
        tempdf = tempdf.rename(columns= {'Cumulative_Total':"Total Box Office"})
        fig = px.bar(tempdf, x = 'Owner', y ='Daily', color = 'Owner', color_discrete_map=color_discrete_map,category_orders={'Owner': category_order}).update_layout(
            yaxis_title = "Total Domestic Box Office ($)", title = "Regulation Summer Movie Auction Podium"
        )
        return fig
    @render_widget
    def ReleaseCostEval():
        df2 = movies.copy()
        df2 = df2.groupby(['Release', 'Owner', 'Price'], as_index=False)['Daily'].sum()
        df2['Price'] = pd.to_numeric(df2['Price'], errors='coerce')
        df2['Daily'] = pd.to_numeric(df2['Daily'], errors='coerce')

        df2['Performance Price'] = df2['Daily']/df2['Price']
        df2 = df2[df2['Price']>0]
        df2 = df2.sort_values(by = 'Performance Price')        
        print(df2)
        fig = px.bar(df2, y = 'Release', x ='Performance Price', color = 'Owner', color_discrete_map=color_discrete_map,category_orders={'Owner': category_order}).update_layout(
            yaxis_title = "Total Domestic Box Office per Point", title = "Movie Cost Performance",  xaxis={'categoryorder':'total descending'}
        )
        return fig
    @render.image
    def image():
        from pathlib import Path

        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "Profile_Pic.jpg"), "width": "400px"}
        return img
    

app = App(app_ui,server)