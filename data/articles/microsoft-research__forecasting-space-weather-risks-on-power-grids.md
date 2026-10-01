---
url: https://www.microsoft.com/en-us/research/blog/forecasting-space-weather-risks-on-power-grids/
title: Forecasting space weather risks on power grids
site: microsoft-research
date: 2026-09-30
scraped_at: 2026-10-01T10:36:04+00:00
---

Published

By

Share this page

During the May 2024 geomagnetic storm, utilities across North America prepared for possible impacts as auroras extended far beyond their usual range. The storm would degrade GPS accuracy and satellite operations, impacting farm operations in North America and Europe. Modern society depends on reliable electric power, yet extreme space-weather events can induce currents in transmission networks that damage equipment and increase operational risk. The challenge is not only knowing that a storm is approaching, but estimating when and where its effects could be most severe with enough warning for grid operators to respond.

During my summer internship at Microsoft Research, I developed a machine learning system that forecasts space-weather risk across 66,935 substations in the continental United States. The system measures how the sun’s activity can affect the earth’s magnetic field and, ultimately, the power grid.  It combines solar-wind observations, forecasts of the Auroral Electrojet (AE) and Disturbance Storm Time (Dst) indices, physics-informed constraints, local geological conductivity, and grid-infrastructure data to produce location-specific risk estimates 30-60 minutes ahead of potential impact.

Space-weather prediction is difficult because it spans several coupled systems. The solar wind changes rapidly, its interaction with Earth’s magnetosphere is irregular, and the resulting ground effects depend on local conditions. Regions with resistive bedrock can experience stronger geomagnetically induced currents (GICs) than regions with more conductive geology. Transmission-line orientation, latitude, and other power-system characteristics further influence the exposure of individual assets.

Stay connected to the research community at Microsoft.

The pipeline addresses this complexity in three stages, shown in Figure 1. First, solar-wind measurements from the L1 Lagrange point are used to generate forecasts of the AE and Dst indices, while geological conductivity and location features are assembled for each substation. Second, a gradient-boosting model combines these forecasted and location-specific inputs to estimate dB/dt, the rate of magnetic-field change associated with GIC risk. Finally, the resulting predictions are converted into location-specific risk estimates and aggregated into a continental risk assessment.  A system of 50 AI agents helped explore features, validation strategies, and model configurations across the pipeline. Only public data sources were used, included NASA OMNI and NASA-aggregated Kyoto World Data Center data, INTERMAGNET and U.S. Geological Survey magnetometer observations, and GridSFM-derived grid data.

The AE predictor was designed to forecast rare, high-intensity geomagnetic activity that drives infrastructure risk. In the 2020-2026 evaluation period, the model produced forecasts spanning nearly the full observed range of AE activity and outperformed several empirical solar-wind-based approaches. The Dst predictor provided an additional signal describing large-scale geomagnetic storm strength. During the most geomagnetically active periods of the 2020-2026 evaluation period, the machine-learning model outperformed the Burton equation on 62.2% of individual hours. The model also produced a substantially wider prediction range than Burton-style approaches and improved severe-event detection in the end-to-end forecasting system by 1.2 percentage points when combined with AE forecasts.

The GIC risk stage was evaluated differently. There is no equivalent widely deployed operational system that provides a direct industry benchmark for this calculation, so the machine learning model was compared with simple linear regression. As Figure 2 shows, the system achieved detection rates of 76.5% for major events (≥10 nT/min), 81.2% for severe events (≥20 nT/min), and 64.1% for extreme events (≥50 nT/min). False-alarm rates increased with storm severity, reflecting the trade-off between missed events and cautious alerts. Performance varied by latitude, with the highest detection rates at northern stations where geomagnetic activity is strongest.

The final stage translates predicted geomagnetic activity into location-specific estimates of dB/dt, the rate of magnetic-field change associated with GIC exposure. Rather than issuing a single alert for the continental United States, the system combines storm conditions with each substation’s latitude and geological factor. This produces continuous risk estimates that can distinguish lower-risk locations from areas where resistive geology can amplify ground-level effects.

Figure 3 illustrates the output for a representative major-storm scenario. The map is a demonstration of the model’s continental-scale output, not a record of a live operational event. It shows how a grid operator or planner could move from a broad space-weather warning toward a more targeted view of which locations may warrant closer analysis. The current pipeline produced estimates for all 66,935 substations in approximately 333 milliseconds during measured inference, allowing many scenarios to be evaluated quickly.

This work demonstrates how physics-grounded machine learning could support more specific and timely assessment of space-weather exposure. Earlier, location-specific information could help utilities prioritize engineering review and consider targeted protective actions, such as adjusting reactive-power reserves or temporarily reconfiguring parts of the network. Further validation with utilities and operational data would be needed before the system could be used in grid operations.

The project also connects with broader Microsoft Research work on AI for power systems. The open grid-data pipeline provided realistic U.S. transmission models, while GridSFM applies deep learning to AC optimal power flow for fast scenario analysis. Together, these efforts point toward richer planning and resilience workflows that combine hazard forecasts, grid topology, and power-flow analysis.

Special thanks to my mentors Weiwei Yang and

for their guidance throughout this project, and to

, and

for their editorial and technical feedback.

Intern
