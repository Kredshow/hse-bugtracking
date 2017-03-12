from urllib import request
import xml.etree.ElementTree as ET
import os
import codecs
from html.parser import HTMLParser


class JiraParser:
    class _JiraHTMLParser(HTMLParser):
        _parsed_data = ""
        _allow_save_data = 0

        def reset_parsed_data(self):
            self._parsed_data = ""

        def get_parsed_data(self):
            return self._parsed_data

        def handle_starttag(self, tag, attrs):
            if tag == "div":
                self._allow_save_data = self._allow_save_data + 1

        def handle_endtag(self, tag):
            if tag == "div":
                self._allow_save_data = self._allow_save_data - 1

        def handle_data(self, data):
            if self._allow_save_data == 0:
                self._parsed_data = self._parsed_data + data

    _base_url = "https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery="
    bugs_catalog_path = "/"

    def __init__(self, set_bugs_catalog_path):
        self.bugs_catalog_path = set_bugs_catalog_path

    def parse_date_period(self, start_date, end_date):
        month_name_to_num = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05",
                             "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10",
                             "Nov": "11", "Dec": "12"}
        html_parser = self._JiraHTMLParser()
        count_bug_reports = 0
        while (count_bug_reports % 1000 == 0):
            if count_bug_reports > 0:
                url = self._base_url + "createdDate%3E=%22" + start_date +\
                      "%2000:00%22+AND+createdDate%3C=%22" + end_date + \
                      "%2023:59%22&tempMax=1000&pager/start=" + \
                      str(count_bug_reports + 1)
            else:
                url = self._base_url + "createdDate%3E=%22" + start_date + \
                      "%2000:00%22+AND+createdDate%3C=%22" + end_date + \
                      "%2023:59%22&tempMax=1000&pager/start=" +\
                      str(count_bug_reports)
            print("Start download XML from:")
            print(url)
            request.urlretrieve(url, "temp_file.xml")
            print("Download finished")
            tree = ET.parse("temp_file.xml")
            root = tree.getroot()[0][6:]
            for child in root:
                count_bug_reports = count_bug_reports + 1
                # Save main bug report information
                date = child.find("created").text
                date = date.split(" ")
                date = date[1] + "." + month_name_to_num[date[2]] + "." + date[3]
                path = self.bugs_catalog_path + date + "/"
                if not os.path.exists(path):
                    os.mkdir(path)
                file_name = child.find("key").attrib["id"]
                file_for_save = open(path + file_name + ".txt", "w")
                file_for_save.write(child.find("summary").text + "\n")

                html_parser.reset_parsed_data()
                html_parser.feed(str(child.find("description").text))
                file_for_save.write(html_parser.get_parsed_data())

                # Save addition information
                path += "/Additional/"
                if not os.path.exists(path):
                    os.mkdir(path)
                file_for_save = codecs.open(path + file_name + ".txt", "w", "utf-8")
                file_for_save.write(child.find("link").text + "\n")
                file_for_save.write(child.find("type").text + "\n")
                file_for_save.write(child.find("priority").text + "\n")


                file_for_save.close()

            if count_bug_reports == 0:
                break
        print("Totally " + str(count_bug_reports) + "bug reports parsed")



if __name__ == '__main__':
    obj = JiraParser("/home/kredshow/PycharmProjects/Bug-tracking/database/")
    obj.parse_date_period("2017/02/20", "2017/02/23")
