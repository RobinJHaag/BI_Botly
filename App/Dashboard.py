from shiny import App, ui, render, reactive
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import sqlite3


def hol_ticket_und_refund_daten():
    dashboard_connector = sqlite3.connect("botly.db")
    tickets = pd.read_sql_query("""
        SELECT p.product_name, d.date_value, c.channel_name
        FROM support_tickets s
        JOIN products p ON s.product_id = p.product_id
        JOIN dates d ON s.date_id = d.date_id
        JOIN channels c ON s.channel_id = c.channel_id
    """, dashboard_connector)
    refunds = pd.read_sql_query("""
        SELECT p.product_name, r.approved, d.date_value
        FROM refund_requests r
        JOIN products p ON r.product_id = p.product_id
        JOIN dates d ON r.date_id = d.date_id
    """, dashboard_connector)
    dashboard_connector.close()
    tickets["date_value"] = pd.to_datetime(tickets["date_value"])
    refunds["date_value"] = pd.to_datetime(refunds["date_value"])
    return tickets, refunds


def simple_plot(title="Demoplot"):
    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor('#001F3F')
    ax.bar(["A", "B", "C"], [5, 7, 3], color="#6A0DAD")
    ax.set_title(title, color='white', fontsize=24)
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.set_facecolor('#001F3F')
    return fig


custom_style = """
<style>
    .nav-link {
        border: 2px solid #CC1E4A !important;
        color: white !important;
        background-color: #001F3F !important;
        margin-right: 10px;
        font-weight: bold;
        border-radius: 4px;
    }

    .nav-link.active, .nav-tabs .nav-item.show .nav-link {
        background-color: #CC1E4A !important;
        color: #001F3F !important;
    }

    .shiny-input-radiogroup {
        margin-top: 24px;
    }

    .form-check {
        margin-top: 4px;
    }
    
    .form-check-input:checked + .form-check-label {
        background-color: #CC1E4A !important;
        color: #001F3F !important;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }

    .form-check-label {
        background-color: #001F3F;
        color: white;
        border: 2px solid #CC1E4A;
        border-radius: 4px;
        margin-right: 10px;
        padding: 6px 12px;
        font-weight: bold;
        cursor: pointer;
    }
</style>
"""

interface = ui.page_fluid(
    ui.HTML(custom_style),
    ui.navset_tab(
        ui.nav_panel("BI Customer Support",
            ui.input_radio_buttons("support_view", "",
                choices=["Ticketübersicht", "Kanalvergleich", "Supportkosten"],
                selected="Ticketübersicht",
                inline=True
            ),
            ui.output_ui("support_view_output")
        ),

        ui.nav_panel("BI Produkte",
            ui.input_radio_buttons("produkt_view", "",
                choices=["Supportkosten pro Produkt", "Refunds & Replacements", "Auffällige Produkte"],
                selected="Supportkosten pro Produkt",
                inline=True
            ),
            ui.output_ui("produkt_view_output")
        ),

        id="dashboard_tabs"
    ),
    style="background-color:#001F3F; padding:30px; width:100%;"
)


def server(input, output, session):
    @render.ui
    def support_view_output():
        match input.support_view():
            case "Ticketübersicht":
                return ui.output_plot("plot_tickets")
            case "Kanalvergleich":
                return ui.HTML("<p style='color:white'>Kanalvergleich kommt später...</p>")
            case "Supportkosten":
                return ui.HTML("<p style='color:white'>Supportkosten-Ansicht in Arbeit...</p>")

    output.support_view_output = support_view_output

    @render.plot
    def plot_tickets():
        return simple_plot("Dummy: Ticketübersicht")

    output.plot_tickets = plot_tickets

    @render.ui
    def produkt_view_output():
        match input.produkt_view():
            case "Supportkosten pro Produkt":
                return ui.output_plot("plot_produktkosten")
            case "Refunds & Replacements":
                return ui.HTML("<p style='color:white'>Refund & Replacement Analyse folgt...</p>")
            case "Auffällige Produkte":
                return ui.HTML("<p style='color:white'>Outlier Detection kommt bald...</p>")

    output.produkt_view_output = produkt_view_output

    @render.plot
    def plot_produktkosten():
        return simple_plot("Dummy: Supportkosten pro Produkt")

    output.plot_produktkosten = plot_produktkosten


app = App(interface, server)
