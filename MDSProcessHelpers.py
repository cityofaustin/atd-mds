import logging
import boto3
import json

from mds import MDSTimeZone
from MDSSchedule import MDSSchedule


class MDSProcess:

    @staticmethod
    def gather_schedule():
        """
        Gathers a list of schedule items based on the time_min and time_max provided values
        :return:
        """
        return

    @staticmethod
    def make_queries_to_provider():
        """
        Uses a list of schedule items to process
        :return:
        """
        return

    @staticmethod
    def save_json_data_to_s3():
        return

    @staticmethod
    def update_schedule_items_successful():
        return

    @staticmethod
    def update_schedule_items_failed():
        """
        Updates a specific schedule, marks it as failed, provides error message,
        data payload (if any),

        :return:
        """
        return

    @staticmethod
    def insert_trip_items_to_db_api():
        """
        Inserts trip items to database
        :return:
        """
        return

    @staticmethod
    def update_slack():
        """
        Send feedback to slack
        :return:
        """
