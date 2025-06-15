from shiny import App, ui, render
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def hol_ticket_und_refund_daten():
    steckdose = sqlite3.connect("botly.db")
    ticket_akte = pd.read_sql_query("""
        SELECT p.product_name, d.date_value
        FROM support_tickets s
        JOIN products p ON s.product_id = p.product_id
        JOIN dates d ON s.date_id = d.date_id
    """, steckdose)
    refund_akte = pd.read_sql_query("""
        SELECT p.product_name, r.approved, d.date_value
        FROM refund_requests r
        JOIN products p ON r.product_id = p.product_id
        JOIN dates d ON r.date_id = d.date_id
    """, steckdose)
    steckdose.close()
    ticket_akte["date_value"] = pd.to_datetime(ticket_akte["date_value"])
    refund_akte["date_value"] = pd.to_datetime(refund_akte["date_value"])
    return ticket_akte, refund_akte


interface = ui.page_fluid(
    ui.h1(ui.span("Botly", style="color:#FF5E3A; font-weight:bold"), " Dashboard – letzte 14 Tage",
          style="color:#FFFFFF; background-color:#001F3F; padding:10px; border-radius:5px; text-align:center;"),
    ui.output_plot("ticket_diagramm"),
    ui.output_plot("refund_diagramm"),
    ui.output_text("refund_rate")
)


def dashboard(inputs, outputs, session):
    @outputs
    @render.plot
    def ticket_diagramm():
        tickets, _ = hol_ticket_und_refund_daten()
        zeitraum_start = datetime.today() - timedelta(days=14)
        letzte = tickets[tickets["date_value"] >= zeitraum_start]
        anzahl_pro_produkt = letzte["product_name"].value_counts()

        fig, ax = plt.subplots(figsize=(20, 12))
        fig.patch.set_facecolor('#001F3F')

        bars = anzahl_pro_produkt.plot(kind="bar", ax=ax, color="#6A0DAD", width=0.6)

        ax.set_title("Support-Tickets je Produkt", fontsize=24, fontweight='bold', color='white', pad=30)
        ax.set_ylabel("Anzahl Tickets", fontsize=18, labelpad=20, color='white')
        ax.set_xlabel("Produkt", fontsize=18, labelpad=20, color='white')

        for bar in bars.patches:
            höhe = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                höhe / 2,
                f'{int(höhe)}',
                ha='center',
                va='center',
                fontsize=18,
                color='white',
                fontweight='bold'
            )

        ax.set_xticklabels(anzahl_pro_produkt.index, rotation=0, fontsize=11, color='white')
        ax.tick_params(axis='x', pad=10, colors='white')
        ax.tick_params(axis='y', colors='white')

        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        plt.subplots_adjust(bottom=0.3, top=0.9, left=0.1, right=0.95)
        plt.tight_layout()
        return fig

    @outputs
    @render.plot
    def refund_diagramm():
        _, refunds = hol_ticket_und_refund_daten()
        zeitraum_start = datetime.today() - timedelta(days=14)
        letzte = refunds[refunds["date_value"] >= zeitraum_start]
        rückgaben = letzte["product_name"].value_counts()

        fig, ax = plt.subplots(figsize=(20, 12))
        fig.patch.set_facecolor('#001F3F')  # Navy background

        bars = rückgaben.plot(kind="bar", ax=ax, color="#FF5E3A", width=0.6)

        ax.set_title("Refunds je Produkt", fontsize=24, fontweight='bold', color='white', pad=30)
        ax.set_ylabel("Anzahl Refunds", fontsize=18, labelpad=20, color='white')
        ax.set_xlabel("Produkt", fontsize=18, labelpad=20, color='white')

        for bar in bars.patches:
            höhe = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                höhe / 2,
                f'{int(höhe)}',
                ha='center',
                va='center',
                fontsize=18,
                color='white',
                fontweight='bold'
            )

        ax.set_xticklabels(rückgaben.index, rotation=0, fontsize=12, color='white')
        ax.tick_params(axis='x', pad=10, colors='white')
        ax.tick_params(axis='y', colors='white')

        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        plt.subplots_adjust(bottom=0.3, top=0.9, left=0.1, right=0.95)
        plt.tight_layout()
        return fig

    @outputs
    @render.text
    def refund_rate():
        tickets, refunds = hol_ticket_und_refund_daten()
        zeitraum_start = datetime.today() - timedelta(days=14)
        t = tickets[tickets["date_value"] >= zeitraum_start]
        r = refunds[refunds["date_value"] >= zeitraum_start]
        if len(t) == 0:
            return "keine tickets gefunden"
        anteil = len(r) / len(t)
        return f"<span style='color:white; padding-left:20px; font-size:18px;'>refund-rate: {round(anteil * 100, 1)} %</span>"

    refund_rate._render_args = {"unsafe_allow_html": True}


app = App(interface, dashboard)
