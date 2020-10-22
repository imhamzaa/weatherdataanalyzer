import argparse
import csv
import datetime
import enum
import glob
import os

from dateutil import parser


class ReportType(enum.Enum):
    YEAR, YEAR_MONTH, One_Line_CHART, Two_Line_Chart = range(1, 5)


class TemperatureUnit(enum.Enum):
    FAHRENHEIT, CELSIUS = 'F', 'C'


class ChartColor(enum.Enum):
    RESET, BLUE, PINK, RED = '\033[0m', '\033[1;34m', '\033[1;35m', '\033[1;31m'


class WeatherModel:

    def __init__(self, reading_line, temp_unit, from_dt_format, to_dt_format):
        max_temp_F, max_temp_C = reading_line['T. Max oF/oC'].split('/')
        min_temp_F, min_temp_C = reading_line['T. Min oF/oC'].split('/')

        self.max_temp = float(max_temp_F) if temp_unit == 'F' else float(max_temp_C)
        self.min_temp = float(min_temp_F) if temp_unit == 'F' else float(min_temp_C)

        self.mean_wind_speed = float(reading_line['Wind Speed (mph)'])
        self.max_wind_speed = float(reading_line['Max Wind Speed (mph)'])

        self.date = datetime.datetime.strptime(reading_line['Date'], from_dt_format).strftime(to_dt_format)


class WeatherMan:
    _temp_unit = 'F'
    _chart_line_style = '*'
    _wind_speed_unit = 'mph'
    _ds_date_format = '%m/%d/%Y'
    _req_date_format = '%Y-%m-%d'

    def __init__(self):
        self.weather_yearly_readings = []
        self.weather_monthly_readings = []
        self.single_chart_monthly_readings = []

    def set_temp_unit(self, unit):
        self._temp_unit = unit

    def set_chart_line_style(self, style):
        self._chart_line_style = style

    def set_data_source_date_format(self, _format):
        self._ds_date_format = _format

    def set_required_date_format(self, _format):
        self._req_date_format = _format

    def validate_path(self, path):
        return path if os.path.isdir(path) else None

    def month_to_month_name(self, month):
        current_date = datetime.datetime.now()
        month = current_date.replace(month=int(month)).strftime('%b')
        return month

    def read_monthly_files(self, path, year_month):
        year, month = year_month.split('/')
        month = self.month_to_month_name(month)
        return self.read_weather_files(path, year, month)

    def read_weather_files(self, path, year, month='*'):
        file_paths = []
        file_path = f'{path}/*{year}_{month}.csv'
        for file_path_ in glob.glob(file_path):
            file_paths.append(file_path_)
        return file_paths

    def read_monthly_readings_from_saved_readings(self, readings, year, month):
        monthly_readings = []
        for reading in readings:
            if f'{year}-{month}-' in reading.date:
                monthly_readings.append(reading)
        return monthly_readings

    def read_weather_values(self, line, weather_readings):
        weather = WeatherModel(line, self._temp_unit, self._ds_date_format, self._req_date_format)
        weather_readings.append(weather)

    def read_weather_file_readings(self, weather_file, weather_readings):
        with open(weather_file, 'r') as file:
            reader = csv.DictReader(file, skipinitialspace=True)
            for line in reader:
                self.read_weather_values(line, weather_readings)

    def populate_weather_readings(self, weather_files):
        weather_readings = []
        for weather_file in weather_files:
            self.read_weather_file_readings(weather_file, weather_readings)
        return weather_readings

    def calculate_highest_temperature(self, readings):
        return max(readings, key=lambda x: x.max_temp)

    def calculate_lowest_temperature(self, readings):
        return min(readings, key=lambda x: x.min_temp)

    def calculate_fastest_wind_speed(self, readings):
        return max(readings, key=lambda x: x.max_wind_speed)

    def calculate_slowest_mean_wind_speed(self, readings):
        return min(readings, key=lambda x: x.mean_wind_speed)

    def calculate_average_high_temp(self, readings):
        temp_sum = sum(c.max_temp for c in readings)
        temp_length = len(readings)
        avg_temp = round(temp_sum / temp_length)
        return avg_temp

    def calculate_average_low_temp(self, readings):
        temp_sum = sum(c.min_temp for c in readings)
        temp_length = len(readings)
        avg_temp = round(temp_sum / temp_length)
        return avg_temp

    def compute_result(self, weather_readings, result_type):
        results = {}
        if result_type == ReportType.YEAR:
            results['HighestTemperature'] = self.calculate_highest_temperature(weather_readings)
            results['LowestTemperature'] = self.calculate_lowest_temperature(weather_readings)
            results['FastestWindSpeed'] = self.calculate_fastest_wind_speed(weather_readings)
            results['SlowestWindSpeed'] = self.calculate_slowest_mean_wind_speed(weather_readings)
        elif result_type == ReportType.YEAR_MONTH:
            results['HighestAverage'] = self.calculate_average_high_temp(weather_readings)
            results['LowestAverage'] = self.calculate_average_low_temp(weather_readings)
        else:
            results = weather_readings

        return results

    def draw_one_line_chart(self, temperature_readings):

        for temperature in temperature_readings:
            day = parser.parse(temperature.date).strftime('%d')

            high_temp_point = round(abs(temperature.max_temp))
            high_temp_value = round(temperature.max_temp)

            low_temp_point = round(abs(temperature.min_temp))
            low_temp_value = round(temperature.min_temp)

            high_temp_line = ChartColor.RED.value + self._chart_line_style * high_temp_point
            low_temp_line = ChartColor.BLUE.value + self._chart_line_style * low_temp_point

            print(
                f'{ChartColor.PINK.value}{day} {low_temp_line}{high_temp_line} {ChartColor.PINK.value}{low_temp_value}{self._temp_unit}-{high_temp_value}{self._temp_unit}')

    def draw_two_line_chart(self, temperature_readings):

        for temperature in temperature_readings:
            day = parser.parse(temperature.date).strftime('%d')

            high_temp_point = round(abs(temperature.max_temp))
            high_temp_value = round(temperature.max_temp)

            low_temp_point = round(abs(temperature.min_temp))
            low_temp_value = round(temperature.min_temp)

            high_temp_line = ChartColor.RED.value + self._chart_line_style * high_temp_point
            low_temp_line = ChartColor.BLUE.value + self._chart_line_style * low_temp_point

            print(
                f'{ChartColor.PINK.value}{day} {high_temp_line}{ChartColor.PINK.value}{high_temp_value}{self._temp_unit}')
            print(
                f'{ChartColor.PINK.value}{day} {low_temp_line}{ChartColor.PINK.value}{low_temp_value}{self._temp_unit}')

    def populate_year_report(self, weather_man_results, year):

        max_temp = weather_man_results['HighestTemperature']
        min_temp = weather_man_results['LowestTemperature']
        fastest_speed = weather_man_results['FastestWindSpeed']
        slowest_speed = weather_man_results['SlowestWindSpeed']

        print(f'Yearly report of {year}:-', end='\n\n')
        print(
            f'Highest temperature: {max_temp.max_temp}{self._temp_unit} on {parser.parse(max_temp.date).strftime("%b %d")}')
        print(
            f'Lowest temperature: {min_temp.min_temp}{self._temp_unit} on {parser.parse(min_temp.date).strftime("%b %d")}')
        print(
            f'Fastest wind speed: {fastest_speed.max_wind_speed} on {parser.parse(fastest_speed.date).strftime("%b %d")}')
        print(
            f'Slowest mean wind speed: {slowest_speed.mean_wind_speed} on {parser.parse(slowest_speed.date).strftime("%b %d")}')

    def populate_one_line_bar_chart_report(self, temperature_readings, year, month):
        print(f'One line Bar Chart for {month} {year}:-\n')
        self.draw_one_line_chart(temperature_readings)

    def populate_two_line_bar_chart_report(self, temperature_readings, year, month):
        # If one-line chart has been drawn, we need to reset color
        print(f'{ChartColor.RESET.value}Two line Bar Chart for {month} {year}:-\n')
        self.draw_two_line_chart(temperature_readings)

    def generate_report(self, weather_man_results, report_type, year='', month=''):
        if report_type == ReportType.YEAR:
            self.populate_year_report(weather_man_results, year)
        elif report_type == ReportType.Two_Line_Chart:
            print('\n\n')
            self.populate_two_line_bar_chart_report(weather_man_results, year, month)
        elif report_type == ReportType.One_Line_CHART:
            print('\n\n')
            self.populate_one_line_bar_chart_report(weather_man_results, year, month)
        else:
            print('No Report to print')

    def saved_month_from_saved_readings(self, path, month_to_search, year_month, year, month):
        readings = []
        reading_files = []
        check_saved_month_from_monthly_readings = any(month_to_search in x.date for x in self.weather_monthly_readings)
        if check_saved_month_from_monthly_readings:
            readings = self.weather_monthly_readings
        else:
            check_saved_year_from_yearly_readings = any(year in x.date for x in self.weather_yearly_readings)
            if check_saved_year_from_yearly_readings:
                readings = self.read_monthly_readings_from_saved_readings(self.weather_yearly_readings, year, month)
            else:
                reading_files = self.read_monthly_files(path, year_month)
        return [readings, reading_files]

    def yearly_weather_report(self, path, year):
        reading_files = self.read_weather_files(path, year)
        if reading_files:
            readings = self.populate_weather_readings(reading_files)
            weather_results = self.compute_result(readings, ReportType.YEAR)
            self.generate_report(weather_results, ReportType.YEAR, year)
            self.weather_yearly_readings = readings
        else:
            print('Yearly weather readings not exist')

    def one_line_chart_weather_report(self, path, year_month):
        year, month = year_month.split('/')
        # To cover cases of month in single/double digit
        month = month if len(month) == 2 else f'0{month}'
        month_to_search = f'-{month}-'

        readings, reading_files = self.saved_month_from_saved_readings(path, month_to_search, year_month, year, month)
        if reading_files or readings:
            if reading_files:
                readings = self.populate_weather_readings(reading_files)
            weather_results = self.compute_result(readings, ReportType.One_Line_CHART)
            month = self.month_to_month_name(month)
            self.generate_report(weather_results, ReportType.One_Line_CHART, year, month)
            self.single_chart_monthly_readings = readings
        else:
            print('Weather readings not exist')

    def two_line_chart_weather_report(self, path, year_month):
        reading_files = []
        year, month = year_month.split('/')
        # To cover cases of month in single/double digit
        month = month if len(month) == 2 else f'0{month}'
        month_to_search = f'-{month}-'

        check_month_from_monthly_one_chart_readings = any(
            month_to_search in x.date for x in self.single_chart_monthly_readings)
        if check_month_from_monthly_one_chart_readings:
            readings = self.single_chart_monthly_readings
        else:
            readings, reading_files = self.saved_month_from_saved_readings(path, month_to_search, year_month, year,
                                                                           month)

        if reading_files or readings:
            if reading_files:
                readings = self.populate_weather_readings(reading_files)
            weather_results = self.compute_result(readings, ReportType.Two_Line_Chart)
            month = self.month_to_month_name(month)
            self.generate_report(weather_results, ReportType.Two_Line_Chart, year, month)
        else:
            print('Weather readings not exist')


weatherman = WeatherMan()
weatherman.set_chart_line_style('&')  # OPTIONAL: Set chart line style
weatherman.set_required_date_format('%Y-%m-%d')  # OPTIONAL: Set required format of date being used in code
weatherman.set_data_source_date_format('%m/%d/%Y')  # OPTIONAL: Set format of date being used in data source
weatherman.set_temp_unit(TemperatureUnit.CELSIUS.value)  # OPTIONAL: Set temperature unit being used in code

arg_parser = argparse.ArgumentParser(description='Weatherman data analysis')
arg_parser.add_argument('path', type=weatherman.validate_path,
                        help='Enter weather files directory path containing .csv files')
arg_parser.add_argument('-e', type=str, default=None,
                        help='(usage: -e yyyy) To see highest temperature and day,'
                             ' lowest temperature and day, fastest wind speed and day'
                             ' and slowest mean wind speed and day of the given year')
arg_parser.add_argument('-s', type=str, default=None,
                        help='(usage: -s yyyy/mm) To see one line horizontal bar charts on the console for'
                             ' the highest and lowest temperature on each day of the given month of year.')
arg_parser.add_argument('-c', type=str, default=None,
                        help='(usage: -c yyyy/mm) To see two line horizontal bar charts on the console for'
                             ' the highest and lowest temperature on each day of the given onth of year.')

input_ = arg_parser.parse_args()
if input_.e:
    weatherman.yearly_weather_report(input_.path, input_.e)
if input_.s:
    weatherman.one_line_chart_weather_report(input_.path, input_.s)
if input_.c:
    weatherman.two_line_chart_weather_report(input_.path, input_.c)
