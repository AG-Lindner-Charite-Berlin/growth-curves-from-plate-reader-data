from dataclasses import dataclass
from typing import Literal, Optional
import pandas as pd


@dataclass
class GrowthCurveConfig:
    # list of measurement series aggregated into one growth curve
    measurement_series: list[str]
    # function to aggregate the measurement series
    aggregation_func: Literal["mean"]
    # short description of the condition
    condition: str
    # which line style the growth curve will be shown in
    line_style: Optional[str] = None
    # which color the growth curve will be shown in
    line_color: Optional[str] = None


class Experiment:
    def __init__(
        self,
        # title of the experiment
        title: str,
        # path to the excel file that contains the raw data
        path_to_raw_data: str,
        # sheet name in the excel file that contains the raw data
        sheet_name: str,
        # measurement period in hours
        measurement_period: int,
        # minimal OD value to be considered as growth (e.g. if set to 0.1, then OD values below 0.1 will be seen as no growth)
        OD_growth_threshold: float,
        # list of GrowthCurveConfig
        growth_curve_configs: list[GrowthCurveConfig],
    ):
        self.title = title
        self.path_to_raw_data = path_to_raw_data
        self.sheet_name = sheet_name
        self.measurement_period = measurement_period
        self.OD_growth_threshold = OD_growth_threshold
        self.growth_curve_configs = growth_curve_configs

        # sets
        self.adjusted_growth_data = self.process_raw_data()

    def process_raw_data(self):
        raw_data = pd.read_excel(
            self.path_to_raw_data, sheet_name=self.sheet_name, index_col=0
        ).dropna()

        return self.adjust_growth_data(raw_data)

    def adjust_growth_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates doubling time from OD data (Excel file) and returns a dataframe

        Parameters:

        file_name: str
            File name of the excel file

        Returns:

        data: pd.DataFrame
        """
        MAGIC_NUMBER = 0.23  # TODO what's this?

        # adjust OD measurements
        raw_data.iloc[:, 1:] = raw_data.iloc[:, 1:] - raw_data.iloc[:, 1:].values.min()
        raw_data.iloc[:, 1:] = (
            raw_data.iloc[:, 1:] / MAGIC_NUMBER
        )  # + inc_OD  # for infinate # TODO i don't understand this

        # convert measurement times (which are in seconds) to hours
        # and set as index for dataframe
        time = raw_data.index.values.astype(float) / 3600
        raw_data.index = time

        return raw_data


from dataclasses import dataclass, field


@dataclass
class PlotConfig:
    y_scale: Literal["linear", "log", "symlog", "logit"]
    x_max: float | None
    y_max: float | None
    is_mean_plot: bool
    save_plot_as: str
    default_line_style: str = "solid"
    default_color_palette: list[str] = field(
        default_factory=lambda: [
            "#e60049",
            "#0bb4ff",
            "#50e991",
            "#e6d800",
            "#9b19f5",
            "#ffa300",
            "#dc0ab4",
            "#b3d4ff",
            "#00bfa0",
        ]
    )
