import streamlit as st
from streamlit_calendar import calendar
import csv
from datetime import datetime
from io import StringIO

class TerminVerwaltung:
    def __init__(self, dateiname):
        self.dateiname = dateiname

    def termin_hinzufuegen(self, datum, beschreibung, teilnehmer):
        try:
            datetime.strptime(datum, "%Y-%m-%d")
        except ValueError:
            st.error("Ungültiges Datumsformat. Bitte verwenden Sie 'YYYY-MM-DD'.")
            return

        termine = self.termine_lesen()
        for termin in termine:
            if termin['start'] == datum:
                termin['title'] = beschreibung
                termin['extendedProps']['teilnehmer'] = ','.join(teilnehmer)
                self.termine_speichern(termine)
                st.success(f"Termin für {datum} wurde aktualisiert.")
                return

        termine.append({
            "title": beschreibung,
            "start": datum,
            "extendedProps": {
                "teilnehmer": ','.join(teilnehmer)
            }
        })
        self.termine_speichern(termine)
        st.success(f"Termin für {datum} wurde erfolgreich hinzugefügt.")

    def termine_lesen(self):
        termine = []
        try:
            with open(self.dateiname, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    termine.append({
                        "title": row[1],
                        "start": row[0],
                        "extendedProps": {
                            "teilnehmer": row[2]
                        }
                    })
        except FileNotFoundError:
            pass
        return termine

    def termine_speichern(self, termine):
        with open(self.dateiname, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for termin in termine:
                writer.writerow([termin['start'], termin['title'], termin['extendedProps']['teilnehmer']])

    def teilnehmer_entfernen(self, datum, zu_entfernender_teilnehmer):
        termine = self.termine_lesen()
        for termin in termine:
            if termin['start'] == datum:
                teilnehmer = termin['extendedProps']['teilnehmer'].split(',')
                if zu_entfernender_teilnehmer in teilnehmer:
                    teilnehmer.remove(zu_entfernender_teilnehmer)
                    termin['extendedProps']['teilnehmer'] = ','.join(teilnehmer)
                    self.termine_speichern(termine)
                    return True
        return False
    
    def teilnehmer_hinzufuegen(self, datum, neuer_teilnehmer):
        termine = self.termine_lesen()
        for termin in termine:
            if termin['start'] == datum:
                teilnehmer = termin['extendedProps']['teilnehmer'].split(',')
                if neuer_teilnehmer not in teilnehmer:
                    teilnehmer.append(neuer_teilnehmer)
                    termin['extendedProps']['teilnehmer'] = ','.join(teilnehmer)
                    self.termine_speichern(termine)
                    return True
        return False

def main():
    st.title("DASU-Boulder-Kalender App")

    verwaltung = TerminVerwaltung("termine.csv")

    # Termine aus der Datei lesen
    events = verwaltung.termine_lesen()

    # Kalenderkonfiguration
    calendar_options = {
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek"
        },
        "initialView": "dayGridWeek",
        "selectable": True,
        "selectMirror": True,
        "dayMaxEvents": True,
        "weekNumbers": True,
        "navLinks": True,
    }

    
    # Kalender anzeigen
    calendar_result = calendar(events=events, options=calendar_options)


    # Ergebnis des Kalenders anzeigen und Teilnehmer verwalten
    if calendar_result:
        if calendar_result['callback'] == 'eventClick':
            selected_event = calendar_result['eventClick']['event']
            if selected_event:
                st.subheader(f"Teilnehmer für {selected_event['title']} am {selected_event['start']}")
                teilnehmer = selected_event['extendedProps']['teilnehmer'].split(',')
                for teilnehmer in teilnehmer:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(teilnehmer)
                    with col2:
                        if st.button("🗑️", key=f"delete_{teilnehmer}"):
                            if verwaltung.teilnehmer_entfernen(selected_event['start'], teilnehmer):
                                st.rerun()

                                # Neuen Teilnehmer hinzufügen
                new_teilnehmer = st.text_input("Neuen Teilnehmer hinzufügen")
                if st.button("Hinzufügen"):
                    if new_teilnehmer:
                        if verwaltung.teilnehmer_hinzufuegen(selected_event['start'], new_teilnehmer):
                            st.success(f"{new_teilnehmer} wurde zum Termin hinzugefügt.")
                            st.rerun()
                    else:
                        st.warning("Bitte geben Sie einen Namen für den neuen Teilnehmer ein.")


    # Alle Termine anzeigen
    # st.subheader("Alle Termine")
    # for event in events:
    #     st.write(f"Datum: {event['start']}, Beschreibung: {event['title']}, Teilnehmer: {event['extendedProps']['teilnehmer']}")

    # Formular zum Hinzufügen eines neuen Termins
    with st.form("neuer_termin"):
        st.write("Neuen Termin hinzufügen")
        datum = st.date_input("Datum")
        # beschreibung = st.text_input("Beschreibung")
        beschreibung = "Bouldern"
        teilnehmer = st.text_input("Teilnehmer (durch Komma getrennt)")
        submit_button = st.form_submit_button("Termin hinzufügen")

        if submit_button:
            verwaltung.termin_hinzufuegen(datum.strftime("%Y-%m-%d"), beschreibung, teilnehmer.split(','))
            st.rerun()

if __name__ == "__main__":
    main()