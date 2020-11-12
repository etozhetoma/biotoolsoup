#!/usr/bin/env python3
__author__ = 'tomarovsky'
'''
Class for determining the coordinates of the pseudoautosomal region.
'''
from Biocrutch.Statistics.coverage_statistics.coverage_metrics import CoveragesMetrics
from collections import Counter


class Coordinator():
    def __init__(self, data, whole_genome_value, deviation_percent):
        self.data = data
        self.whole_genome_value = whole_genome_value
        self.minimum_coverage = whole_genome_value - (whole_genome_value / 100 * deviation_percent)
        self.maximum_coverage = whole_genome_value + (whole_genome_value / 100 * deviation_percent)
        self.median_between_regions_list = []
        self.coordinates = []

    @staticmethod
    def coordinates_between_regions(coordinates: list, between_regions_list: list) -> list:
        # input list [[start, stop], [start, stop]]
        last_element_index = len(coordinates) - 1
        for lst in range(len(coordinates)):
            start = coordinates[lst][-1]
            if lst == last_element_index:
                break
            stop = coordinates[lst + 1][0]
            between_regions_list.append([start, stop])
        return between_regions_list


    def get_coordinates(self,
                    coverage_column_name: int,
                    window_column_name: int,
                    repeat_window_number: int) -> list:
        self.coordinates = []
        repeat_window = 0
        start_coordinate = None

        between_regions_coverage_dict = Counter()
        between_region_flag = None

        for ln in self.data:
            line = ln.rstrip().split("\t")
            coverage_value = float(line[coverage_column_name])
            current_window = int(line[window_column_name])

            if between_region_flag:
                between_regions_coverage_dict[coverage_value] += 1

            if coverage_value > self.minimum_coverage:  # and coverage_value < self.maximum_coverage:
                repeat_window += 1
                if repeat_window == repeat_window_number and start_coordinate is None:
                    start_coordinate = current_window - repeat_window + 1  # * args.window_size
                    repeat_window = 0
            elif start_coordinate is not None and (coverage_value <= self.minimum_coverage or coverage_value >= self.maximum_coverage):
                stop_coordinate = current_window - 1  # * args.window_size
                self.coordinates.append([start_coordinate, stop_coordinate])
                if between_region_flag:
                    self.median_between_regions_list.append(CoveragesMetrics(between_regions_coverage_dict).median_value())
                    between_regions_coverage_dict.clear()
                if self.coordinates:
                    between_region_flag = True
                start_coordinate = None
                repeat_window = 0
            else:
                repeat_window = 0
        if self.coordinates[-1][-1] != current_window:
            self.coordinates.append([(stop_coordinate + 1), current_window])
        if between_regions_coverage_dict:
            self.median_between_regions_list.append(CoveragesMetrics(between_regions_coverage_dict).median_value())
            between_regions_coverage_dict.clear()
        
        # print(self.median_between_regions_list)
        # print(self.coordinates)
        return self.coordinates
