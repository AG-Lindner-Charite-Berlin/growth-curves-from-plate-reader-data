# growth-figures

Use this script for the analysis of data from the growth experiments.

## How to Use

0. Download this repository.
1. Make sure that Python is installed.
2. Open the folder of this repository in your terminal.
3. Run `pip install -r requirements.txt` to install all required packages.
4. Create a folder called `data` and put all raw data to be analysed into this folder
5. For easiest use, create a json file describing your plate layout. It should be formatted as follows:

```json
[
  {
    "condition": "",
    "strain": "",
    "medium": "",
    "replicate": "",
    "well": ""
  }
]
```

Example

```json
[
  {
    "condition": "",
    "strain": "Maxkat",
    "medium": "Glucose",
    "replicate": "1",
    "well": "A1"
  },
  {
    "condition": "",
    "strain": "Maxkat",
    "medium": "Glycerol",
    "replicate": "2",
    "well": "A2"
  }
]
```

6. Open the script `Plotting Script.ipynb` and click on "Run all"

## Troubleshooting

I'm always happy to help - just shoot me an email (mail@timonschneider.de).

## Credits

Original Script Author: https://github.com/he-hai

## Comments Workshop

- integrate media variable into more general _conditions_ variable (Jan)
- allow for more replicates
- Explain this:

  ```python
  configs_MiniKat_without_IPTG = [
      GrowthCurveConfig(
          measurement_series=[
              "A1",
              "A2",
          ],
          aggregation_func="mean",
          condition="Ace30",
      ),
  ]

  experiment = Experiment(
      title="2023_05_23 MiniKat MX IBA IBU BDO, MiniKat #1 without IPTG",
      path_to_raw_data="data/2023_05_23 MiniKat MX IBA IBU BDO.xlsx",
      sheet_name="Sheet1",
      growth_curve_configs=configs_MiniKat_without_IPTG,
      measurement_period=10,
      OD_growth_threshold=0.05,
  )

  plot_config = PlotConfig(
      y_scale="linear",
      x_max=None,
      y_max=None,
      save_plot_as="png",
      is_mean_plot=True,
  )

  plot_no_numbers(
      experiment=experiment,
      plot_config=plot_config,
  )
  ```

  - If you make changes to any other files than the current notebook you have to restart kernel
  - Line style changes must be more accessible
  - data folder with subfolders explanation in README
  - explain where and how to change colors
  - [ ] Allow for flexible well properties
    - [ ] Extend groupby functionality accordingly
  - Show how to plot specific number of hours/adjust x scale

# ToDo

- Measurement period is not used???
