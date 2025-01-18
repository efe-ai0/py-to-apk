from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import requests
from datetime import datetime
import pytz

# API Ayarları
API_KEY = "7bb0d1e7776b1aff18253704fcc96df9"
BASE_URL = "https://v3.football.api-sports.io/"

# Lig ID'leri
LEAGUES = {
    "Premier League": 39,
    "La Liga": 140,
    "Bundesliga": 78,
    "Serie A": 135,
    "Ligue 1": 61,
    "Süper Lig": 203
}

# Türkiye saat dilimi
turkey_tz = pytz.timezone('Europe/Istanbul')

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.league_spinner = Spinner(
            text="Ligi Seç",
            values=list(LEAGUES.keys()),
            size_hint=(1, 0.2)
        )
        layout.add_widget(self.league_spinner)

        button_layout = BoxLayout(size_hint=(1, 0.2))

        standings_button = Button(text="Puan Durumu", on_press=self.show_standings)
        fixture_button = Button(text="Fikstür", on_press=self.show_fixtures)

        button_layout.add_widget(standings_button)
        button_layout.add_widget(fixture_button)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def show_standings(self, instance):
        league_name = self.league_spinner.text
        if league_name == "Ligi Seç":
            self.manager.get_screen("results").display_message("Lütfen bir lig seçin.")
        else:
            self.manager.current = "results"
            self.manager.get_screen("results").fetch_league_standings(league_name)

    def show_fixtures(self, instance):
        league_name = self.league_spinner.text
        if league_name == "Ligi Seç":
            self.manager.get_screen("results").display_message("Lütfen bir lig seçin.")
        else:
            self.manager.current = "results"
            self.manager.get_screen("results").fetch_fixtures(league_name)

class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.results_area = ScrollView(size_hint=(1, 0.8))
        self.results_layout = GridLayout(cols=1, size_hint_y=None, spacing=10)
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        self.results_area.add_widget(self.results_layout)

        layout.add_widget(self.results_area)

        back_button = Button(text="Geri Dön", size_hint=(1, 0.2), on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        self.manager.current = "menu"

    def fetch_league_standings(self, league_name):
        league_id = LEAGUES.get(league_name)
        url = f"{BASE_URL}standings?league={league_id}&season=2023"
        headers = {"x-apisports-key": API_KEY}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            standings = data.get('response', [])[0].get('league', {}).get('standings', [[]])[0]
            self.display_standings(standings)
        else:
            self.display_message("Puan durumu getirilemedi.")

    def fetch_fixtures(self, league_name):
        league_id = LEAGUES.get(league_name)
        url = f"{BASE_URL}fixtures?league={league_id}&season=2023&next=5"
        headers = {"x-apisports-key": API_KEY}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get('response', [])
            self.display_fixtures(fixtures)
        else:
            self.display_message("Fikstür getirilemedi.")

    def display_standings(self, standings):
        self.results_layout.clear_widgets()
        self.results_layout.add_widget(Label(text="Puan Durumu", size_hint_y=None, height=40))

        for team in standings:
            team_name = team['team']['name']
            points = team['points']
            label = Label(text=f"{team_name}: {points} puan", size_hint_y=None, height=30)
            self.results_layout.add_widget(label)

    def display_fixtures(self, fixtures):
        self.results_layout.clear_widgets()
        self.results_layout.add_widget(Label(text="Fikstür", size_hint_y=None, height=40))

        for fixture in fixtures:
            date_str = fixture['fixture']['date']
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00')).astimezone(turkey_tz)
            home_team = fixture['teams']['home']['name']
            away_team = fixture['teams']['away']['name']
            formatted_date = date_obj.strftime("%d %B %Y, %H:%M")
            label = Label(text=f"{formatted_date} - {home_team} vs {away_team}", size_hint_y=None, height=30)
            self.results_layout.add_widget(label)

    def display_message(self, message):
        self.results_layout.clear_widgets()
        self.results_layout.add_widget(Label(text=message, size_hint_y=None, height=40))

class FutbolApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainMenuScreen(name="menu"))
        sm.add_widget(ResultsScreen(name="results"))
        return sm

if __name__ == "__main__":
    FutbolApp().run()
