# Bayesian Data Analysis for CO2 Prediction

This was a project for predicting the CO2 emissions of a given country using a hierearchical beta model, utilizing `brms` and `cmdstanr`. The dataset originally had over 50 initial variables, but was skimmed down to the 16 most relevant. The resulting model was highly accurate, as is indicated by the resulting plots in the images folder.
Although unintentional, the paper ended up supporting and making use of the Environmental Kuznets Curve (https://www.sciencedirect.com/topics/earth-and-planetary-sciences/environmental-kuznets-curve) hypothesis, showcasing the logarithmic relationship between CO2 emissions and GDP-per-capita.

## Prerequisites
Before running the analysis, ensure that the following R packages are installed:
- `tidybayes`
- `dplyr`
- `brms`
- `cmdstanr`
- `ggplot2`

## Setup
### 1. Install CmdStan (if not installed)
CmdStan is required for Bayesian modeling. If not installed, the script automatically installs it:
```r
cmdstan_installed <- function(){
  res <- try(out <- cmdstanr::cmdstan_path(), silent = TRUE)
  !inherits(res, "try-error")
}
if(!cmdstan_installed()){
  install_cmdstan()
}
```

### 2. Load Data
The dataset is read from `data.csv` in the `notebooks/BDA Project` folder:
```r
data <- read.csv("notebooks/BDA Project/data.csv")
```

## Data Preprocessing
### Feature Engineering
Several new features are created:
- **GDP per capita** (`gdp_perc`)
- **Land usage percentages** (urban, rural, agricultural, forest)
- **Population percentages** (urban, rural)
- **Greenhouse gas emissions per capita** (CO2, methane, nitrous oxide, other emissions)

### Dropping Unnecessary Columns
A list of non-essential columns (e.g., electricity production, land area, currency, political attributes) is defined and removed to streamline the dataset.

### Removing Countries with Significant Missing Data
Certain countries with extensive missing values are filtered out.

### Normalization
GDP per capita (`gdp_perc`) is normalized:
```r
df$gdp_perc_normalized <- normalize(df$gdp_perc)
```

## Exploratory Data Analysis
A scatter plot is created to examine the relationship between GDP per capita and CO2 emissions per capita:
```r
ggplot(df, aes(x = gdp_perc, y = co2_emissions_perc)) +
  geom_point(alpha = 0.7, color = "blue") +  # Points
  geom_smooth(method = "lm", se = TRUE, color = "red", linetype = "dashed") +  # Regression line
  scale_x_log10() +  # Logarithmic scale for x-axis
  scale_y_log10() +  # Logarithmic scale for y-axis
  labs(
    title = "Log-Log Relationship Between CO2 Emissions Per Capita and GDP Per Capita",
    x = "Log(GDP Per Capita)",
    y = "Log(CO2 Emissions)"
  ) +
  theme_minimal()
```

## Bayesian Beta Regression Model
A Bayesian beta regression model is used to predict log CO2 emissions per capita:
```r
formula <- bf(
  log(co2_emissions_perc) ~ 1
  + log(gdp_perc) 
  + I(log(gdp_perc)^2) 
  + log(urban_population_pct) 
  + log(self_employed_pct) 
  + log(vulnerable_employment_pct) 
  + log(median_age) 
  + log(birth_rate) 
  + log(life_expectancy),
  family = Beta(link="log"),
  center = FALSE
)
```

### Priors
- **Informative priors** for GDP per capita:
  ```r
  prior(normal(0.8, 0.3), class = "b", coef = "loggdp_perc")  
  prior(normal(-0.1, 0.05), class = "b", coef = "Iloggdp_percE2")
  ```
- **Uninformative priors** for other predictors:
  ```r
  prior(normal(0, 1), class="b", coef="logurban_population_pct")
  ```

### Model Fitting
The model is trained with `brm()`:
```r
fit <- brm(
  formula = formula,
  prior = priors,
  data = df,
  chains = 4,
  warmup = 2000,
  iter = 5000,
  cores = parallel::detectCores()
)
```

### Model Evaluation
- Posterior predictive checks:
  ```r
  pp_check(beta, ndraws = 100)
  ```
- Leave-One-Out (LOO) cross-validation:
  ```r
  loo(beta)
  ```
- Identifying countries with problematic Pareto k values:
  ```r
  df[which(loo(beta)$diagnostics$pareto_k > 0.7), ]$country
  ```

## Summary
This project conducts Bayesian modeling on CO2 emissions per capita using GDP per capita and other socio-economic factors. It follows a structured pipeline: data preprocessing, exploratory analysis, Bayesian regression modeling, and model evaluation. The approach ensures a rigorous statistical framework for understanding the relationship between economic indicators and environmental impact.

