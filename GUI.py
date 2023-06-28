import sys
import folium
from main import dijkstra_run, radius_run2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folium Map in GUI")
        self.setGeometry(100, 100, 800, 600)

        # Create a QWidget to hold the QWebEngineView widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a QVBoxLayout to hold the QWebEngineView
        layout = QVBoxLayout(self.central_widget)

        # Create a QWebEngineView widget
        self.webview = QWebEngineView()

        # Add the QWebEngineView to the layout
        layout.addWidget(self.webview)

        # Initialize the Folium map
        self.map = folium.Map(location=[52.07858904204588, 4.309522201318987], zoom_start=10)

        # Load the initial map HTML content
        self.update_map()

    def update_map(self):

        # Input for the coördinates and city
        print('Give us your starting point')
        latitude_start = float(input("start latitude: "))
        longitude_start = float(input("start longitude: "))
        print('Give us your end point')
        latitude_end = float(input("end latitude: "))
        longitude_end = float(input("end longitude: "))
        print('Give us the name of your desired city: ')
        city_name = input('City: ')

        # Create a new Folium map with the start input latitude and longitude
        self.map = folium.Map(location=[longitude_start, latitude_start], zoom_start=14)

        # Plot out routes on the Folium map
        place_name = city_name + ", The Netherlands"
        print(place_name)
        loc3 = radius_run2((latitude_start, longitude_start), (latitude_end, longitude_end), place_name)
        loc2 = dijkstra_run((latitude_start, longitude_start), (latitude_end, longitude_end), place_name)

        folium.PolyLine(loc3, color='green', weight=10, opacity=0.8).add_to(self.map)
        folium.PolyLine(loc2, color='red', weight=10, opacity=0.8).add_to(self.map)


        # Get the HTML string of the map
        map_html = self.map.get_root().render()

        # Load the updated map HTML content into the QWebEngineView
        self.webview.setHtml(map_html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MapWindow()
    window.show()
    sys.exit(app.exec_())

# (4.222412, 52.068849), (4.325155, 52.081432)
# kijkduin                den haag centraal
