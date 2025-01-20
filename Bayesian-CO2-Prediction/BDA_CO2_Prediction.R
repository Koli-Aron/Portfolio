library(tidybayes)
library(dplyr)
library(brms)
library(cmdstanr)
library(tidybayes)
library(ggplot2)


# Some additional set-up to make plots legible
ggplot2::theme_set(theme_minimal(base_size = 14))

cmdstan_installed <- function(){
  res <- try(out <- cmdstanr::cmdstan_path(), silent = TRUE)
  !inherits(res, "try-error")
}
if(!cmdstan_installed()){
  install_cmdstan()
}






#setwd(".../BDA Project") # Path to directory
data <- read.csv("notebooks/BDA Project/data.csv")


# Creating new columns
data <- data %>%
  mutate(
    # Create a column for GDP per capita
    gdp_perc = gdp / population,
    
    # Land percentages
    total_land = urban_land + rural_land + forest_area + agricultural_land,
    urban_pct = urban_land / total_land,
    rural_pct = rural_land / total_land,
    agricultural_pct = agricultural_land / total_land,
    forest_pct = forest_area / total_land,
    
    # Population percentages
    urban_population_pct = urban_population / population,
    rural_population_pct = rural_population / population, 
    
    # Add columns for per capita green house emissions
    co2_emissions_perc = co2_emissions / population,
    methane_emissions_perc = methane_emissions / population,
    nitrous_oxide_emissions_perc= nitrous_oxide_emissions / population,
    greenhouse_other_emissions_perc = greenhouse_other_emissions / population,
    
  )


# Creating a list of unnecessary columns
drop <- {
  c(
    "alternative_nuclear_energy_pct",
    "electricty_production_coal_pct",
    "electricty_production_hydroelectric_pct",
    "electricty_production_gas_pct",
    "electricty_production_nuclear_pct",
    "electricty_production_oil_pct",
    "electricty_production_renewable_pct",
    "energy_imports_pct",
    "fossil_energy_consumption_pct",
    "urban_land",
    "rural_land",
    "land_area",
    "gdp",
    "country_long",
    "currency",
    "capital_city",
    "demonym",
    "latitude",
    "longitude",
    "central_government_debt_pct_gdp",
    "expense_pct_gdp",
    #"self_employed_pct",
    "tax_revenue_pct_gdp",
    #"vulnerable_employment_pct",
    "urban_population_under_5m",
    "health_expenditure_pct_gdp",
    "health_expenditure_capita",
    "hospital_beds",
    "hiv_incidence",
    "suicide_rate",
    "armed_forces",
    "internally_displaced_persons",
    "military_expenditure_pct_gdp",
    "death_rate",
    "internet_pct",
    "net_migration",
    "population_female",
    "population_male",
    "women_parliament_seats_pct",
    "press",
    "democracy_type",
    "political_leader",
    "title",
    "central_government_debt_pct_gdp",
    "expense_pct_gdp"
  )
} 

df <-
  data[, !(names(data) %in% drop)] # Dropping columns included in the list

# Dropping countries with a significant portion of missing data
df <- df %>%
  filter(
    !country %in% c(
      "San Marino",
      "Monaco",
      "Marshall Islands",
      "Andorra",
      "Liechtenstein",
      "Seychelles",
      "St. Kitts and Nevis",
      "Tuvalu",
      "Kiribati",
      "Antigua and Barbuda",
      "West Bank and Gaza",
      "Palau",
      # Drop for missing gdp :)
      "Dem. People's Rep. Korea"
    )
  )

normalize <- function(x, na.rm=TRUE) {
  return((x- min(x, na.rm=na.rm)) /(max(x, na.rm=na.rm)-min(x, na.rm=na.rm)))
}

library(ggplot2)


# Normalize gdp_perc
df$gdp_perc_normalized <- normalize(df$gdp_perc)

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

#Justification for using loggdp_perc as a prior
log_fit <- lm(log(co2_emissions_perc) ~ log(gdp_perc), data = df)
regular_fit <- lm(log(co2_emissions_perc) ~ gdp_perc, data = df)
summary(log_fit)
summary(regular_fit)




beta_model <- function() {
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
  
  
  priors <- c(
    # Informative
    prior(normal(0.8, 0.3), class = "b", coef = "loggdp_perc"),  
    prior(normal(-0.1, 0.05), class = "b", coef = "Iloggdp_percE2"),
    
    # Uninformative priors
    prior(normal(0, 1), class="b", coef="logurban_population_pct"),
    prior(normal(0, 1), class="b", coef="logbirth_rate"),
    prior(normal(0, 1), class="b", coef="loglife_expectancy"),
    prior(normal(0, 1), class="b", coef="logmedian_age"),
    prior(normal(0, 1), class="b", coef="logself_employed_pct")
  )
  fit <- brm(
    formula = formula ,
    prior = priors,
    data = df,
    
    chains=4,
    warmup=2000,
    iter=5000,
    cores = parallel::detectCores() 
  )
  
  fit <- add_criterion(
    fit,
    criterion = "loo"
  )
  return(fit)
}


beta <- beta_model
pp_check(beta, ndraws = 100)
loo(beta)


# Countries with problematic pareto_k
df[which(loo(beta)$diagnostics$pareto_k > 0.7), ]$country

#pp_check(b_model)  # Histogram of observed vs. predicted
