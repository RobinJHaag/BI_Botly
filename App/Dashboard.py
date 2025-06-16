from shiny import App, ui as interface, render, reactive
import matplotlib.pyplot as plotter
import pandas as kungfu_panda
import sqlite3
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
import warnings

warnings.filterwarnings("ignore")


def zieh_supportkosten_pro_sale():
    steckdose_lmfao = sqlite3.connect("botly.db")
    tabelle_kosten_xd = kungfu_panda.read_sql_query("""
        SELECT p.product_name,
               p.price,
               SUM(s.handling_time_minutes / 60.0 * e.hourly_wage) AS kosten,
               COUNT(v.sale_id) AS sales
        FROM support_tickets s
        JOIN products p ON s.product_id = p.product_id
        JOIN support_employees e ON s.employee_id = e.employee_id
        LEFT JOIN sales v ON p.product_id = v.product_id
        GROUP BY p.product_name, p.price
        HAVING sales > 0
    """, steckdose_lmfao)
    steckdose_lmfao.close()
    tabelle_kosten_xd["kosten_pro_sale"] = tabelle_kosten_xd["kosten"] / tabelle_kosten_xd["sales"]
    return tabelle_kosten_xd.nlargest(10, "kosten_pro_sale")


def zieh_ticket():
    db_lol = sqlite3.connect("botly.db")
    basisdaten_xd = kungfu_panda.read_sql_query("""
        SELECT p.product_name, d.date_value, c.channel_name
        FROM support_tickets s
        JOIN products p ON s.product_id = p.product_id
        JOIN dates d ON s.date_id = d.date_id
        JOIN channels c ON s.channel_id = c.channel_id
    """, db_lol)
    db_lol.close()
    basisdaten_xd["date_value"] = kungfu_panda.to_datetime(basisdaten_xd["date_value"])
    return basisdaten_xd


def zieh_und_gruppiere():
    grundlage_rofl = zieh_ticket()
    return grundlage_rofl.groupby(["product_name", "date_value"]).size().reset_index(name="anzahl")


def zieh_ziitruum(tage):
    ganze_liste = zieh_ticket()
    ab_tag = datetime.today() - timedelta(days=tage)
    return ganze_liste[ganze_liste["date_value"] >= ab_tag]


def zieh_supportkosten_top():
    connection_rofl = sqlite3.connect("botly.db")
    teuer_lol = kungfu_panda.read_sql_query("""
        SELECT p.product_name, SUM(s.handling_time_minutes/60.0 * e.hourly_wage) AS kosten
        FROM support_tickets s
        JOIN products p ON s.product_id = p.product_id
        JOIN support_employees e ON s.employee_id = e.employee_id
        GROUP BY p.product_name
    """, connection_rofl)
    connection_rofl.close()
    return teuer_lol.nlargest(10, 'kosten')


def iqr_grenze(xd_serie):
    q1, q3 = xd_serie.quantile([0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)


css = """
<style>
    .nav-link { border:2px solid #7851A9!important; color:white!important; background:#001F3F!important; margin-right:10px; font-weight:bold; border-radius:4px; }
    .nav-link.active { background:#7851A9!important; color:#001F3F!important; }
</style>
"""

oberflaeche = interface.page_fluid(
    interface.HTML(css),
    interface.navset_tab(
        interface.nav_panel("Tickets",
                            interface.output_ui("tickets_panel"),
                            interface.input_radio_buttons("zeitraum", "Zeitraum:",
                                                          choices=["14 Tage", "7 Tage", "Prognose"], selected="14 Tage",
                                                          inline=True)
                            ),

        interface.nav_panel("Supportkosten pro Produkt",
                            interface.output_plot("kosten_produkt")
                            ),
        interface.nav_panel("Kanalvergleich",
                            interface.output_plot("kanal_plot"),
                            interface.output_plot("workforce_plot")
                            )
    ),
    style="background-color:#001F3F; padding:20px;"
)


def server(input, output, session):
    @reactive.calc
    def zeitraum_wahl():
        wahl = input.zeitraum()
        return 14 if wahl == "14 Tage" else 7 if wahl == "7 Tage" else None

    @render.ui
    def tickets_panel():
        if input.zeitraum() == "Prognose":
            return interface.div(interface.output_ui("forecast_warnung"), interface.output_plot("ticket_forecast"),
                                 style="padding:20px")
        return interface.div(interface.output_plot("ticket_chart"), interface.HTML(warnung_xd()), style="padding:20px")

    def warnung_xd():
        wie_viele = zeitraum_wahl() or 14
        daten_xd = zieh_ziitruum(wie_viele)
        gezählt = daten_xd["product_name"].value_counts().head(10)
        grenze = iqr_grenze(gezählt)
        auffaellig = [x for x, y in gezählt.items() if y > grenze]
        return f"<p style='color:#FF5E3A; font-weight:bold;'>⚠ Ungewöhnlich: {', '.join(auffaellig)}</p>" if auffaellig else ""

    @render.plot
    def ticket_chart():
        d = zeitraum_wahl() or 14
        rofl_daten = zieh_ziitruum(d)
        zahlen = rofl_daten["product_name"].value_counts().head(10)
        gr = iqr_grenze(zahlen)
        farben = ["#7851A9" if v <= gr else "#FF5E3A" for v in zahlen.values]
        fig, klotz = plotter.subplots(figsize=(12, 4));
        fig.patch.set_facecolor('#001F3F')
        teile = klotz.bar(zahlen.index, zahlen.values, color=farben)
        klotz.set_title(f"Tickets pro Produkt ({d} Tage)", color='white')
        klotz.tick_params(colors='white')
        for s in klotz.spines.values(): s.set_color('white')
        for b in teile: klotz.text(b.get_x() + b.get_width() / 2, b.get_height() / 2, int(b.get_height()), ha='center',
                                   color='white')
        plotter.tight_layout();
        return fig

    @render.ui
    def forecast_warnung():
        daten = zieh_und_gruppiere()
        top2 = daten.groupby("product_name")["anzahl"].sum().nlargest(2).index
        wtf = []
        for p in top2:
            serie = daten[daten["product_name"] == p].set_index("date_value")["anzahl"].asfreq('D', fill_value=0)
            zukunft = ARIMA(serie, order=(2, 1, 2)).fit().forecast(7)
            if zukunft.sum() > 230: wtf.append(p)
        return interface.HTML(
            f"<p style='color:#FF5E3A; font-weight:bold; text-align:center;'>⚠ Prognose hoch: {', '.join(wtf)}</p>") if wtf else ""

    @render.plot
    def ticket_forecast():
        stuff = zieh_und_gruppiere()
        top2 = stuff.groupby("product_name")["anzahl"].sum().nlargest(2).index
        fig, ax_liste = plotter.subplots(len(top2), 1, figsize=(10, 5), squeeze=False)
        fig.patch.set_facecolor('#001F3F')
        for i, p in enumerate(top2):
            serie = stuff[stuff["product_name"] == p].set_index("date_value")["anzahl"].asfreq('D', fill_value=0)
            f = ARIMA(serie, order=(5, 1, 5)).fit().forecast(7) * 1.1
            ax = ax_liste[i, 0]
            ax.text(0, 1.02, f" Erwartete Tickets: {int(f.sum())}", transform=ax.transAxes, ha='left', va='bottom',
                    fontsize=10, color='#fd5e53', fontweight='bold')
            teile = ax.bar(f.index, f.values, color="#FF5E3A", alpha=0.8)
            for b in teile: ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 0.15, int(b.get_height()),
                                    ha='center', color='white')
            ax.plot(f.index, f.values, color="#7851A9", linewidth=2)
            ax.set_title(p, color='#FF5E3A')
            ax.tick_params(colors='white')
            for s in ax.spines.values(): s.set_color('white')
        fig.suptitle("Ticket-Prognose (Top 2)", color='white', fontsize=14)
        plotter.tight_layout(rect=[0, 0, 1, 0.93])
        return fig

    @render.plot
    def kanal_plot():
        daten = zieh_ziitruum(zeitraum_wahl() or 14)
        kanal_ding = daten["channel_name"].value_counts()
        fig, klotz = plotter.subplots(figsize=(8, 4));
        fig.patch.set_facecolor('#001F3F')
        teile = klotz.bar(kanal_ding.index, kanal_ding.values, color="#7851A9")
        klotz.set_title("Tickets pro Kanal", color='white')
        klotz.tick_params(colors='white')
        for s in klotz.spines.values(): s.set_color('white')
        for b in teile: klotz.text(b.get_x() + b.get_width() / 2, b.get_height() / 2, int(b.get_height()), ha='center',
                                   color='white')
        plotter.tight_layout();
        return fig

    @render.plot
    def workforce_plot():
        dat = zieh_ticket().groupby('date_value').size().asfreq('D', fill_value=0)
        f = ARIMA(dat, order=(2, 1, 2)).fit().forecast(7) * 1.1
        f = f.clip(lower=0)
        fig, klotz = plotter.subplots(figsize=(10, 4))
        fig.patch.set_facecolor('#001F3F')
        teile = klotz.bar(f.index, f.values, color="#FF5E3A", alpha=0.8)
        schichten = (f / 8).apply(lambda x: int(x // 1 + 2))
        for b, h, s in zip(teile, f.values, schichten):
            klotz.text(b.get_x() + b.get_width() / 2, h * 0.15, int(h), ha='center', color='white')
            klotz.text(b.get_x() + b.get_width() / 2, h * 0.05, f"{int(s)} Schichten", ha='center', color='white',
                       fontsize=9, fontweight='bold')
        klotz.plot(f.index, f.values, color="#7851A9", linewidth=2)
        klotz.set_title("Workforce Forecast", color='white')
        klotz.tick_params(colors='white')
        for s in klotz.spines.values(): s.set_color('white')
        plotter.tight_layout()
        return fig

    @render.plot
    def kosten_produkt():
        zahlen = zieh_supportkosten_pro_sale().nlargest(8, "kosten_pro_sale")
        fig, klotz = plotter.subplots(figsize=(14, 6))
        fig.patch.set_facecolor('#001F3F')
        farben = []
        warn_lol = []
        for _, r in zahlen.iterrows():
            if r["kosten_pro_sale"] > 0.15 * r["price"]:
                farben.append("#FF5E3A")
                warn_lol.append(True)
            else:
                farben.append("#7851A9")
                warn_lol.append(False)
        teile = klotz.bar(zahlen['product_name'], zahlen['kosten_pro_sale'], color=farben)
        klotz.set_title("Supportkosten pro Produkt (Top 8)", color='white')
        klotz.set_ylabel("CHF", color='white')
        klotz.tick_params(colors='white')
        for s in klotz.spines.values(): s.set_color('white')
        for b, (_, r), warnung in zip(teile, zahlen.iterrows(), warn_lol):
            h = r['kosten_pro_sale']
            klotz.text(b.get_x() + b.get_width() / 2, h * 0.5, f"{h:.2f} CHF", ha='center', color='white', fontsize=9)
            if warnung:
                klotz.text(b.get_x() + b.get_width() / 2, h * 1, "⚠ Evaluation nötig", ha='center', va='bottom',
                           color='#FF5E3A', fontsize=8, fontweight='bold')
        plotter.tight_layout()
        return fig


app = App(oberflaeche, server)
