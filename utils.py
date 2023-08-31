import pandas as pd
import numpy as np


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces; convert other spaces to
    underscores; and remove anything that is not an alphanumeric, dash,
    underscore, or dot.
    Adapted from Django Framework, utils/text.py
    """
    import re

    s = str(s).splitlines()[0]
    s = s.strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    s = re.sub("mathit", "", s)
    return re.sub("Delta_", "D", s)


def adjust_growth_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates doubling time from OD data (Excel file) and returns a dataframe

    Parameters:

    file_name: str
        File name of the excel file

    Returns:

    data: pd.DataFrame
    """
    OD_correction = (
        0.23  # Experimentally determined correction from measured to actual OD
    )

    # adjust OD measurements
    raw_data.iloc[:, 1:] = raw_data.iloc[:, 1:] - raw_data.iloc[:, 1:].values.min()
    raw_data.iloc[:, 1:] = (
        raw_data.iloc[:, 1:] / OD_correction
    )  # + inc_OD  # for infinate # TODO i don't understand this

    # convert measurement times (which are in seconds) to hours
    # and set as index for dataframe
    time = raw_data.index.values.astype(float) / 3600
    raw_data.index = time

    return raw_data
