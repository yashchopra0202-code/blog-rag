---
url: https://www.microsoft.com/en-us/research/blog/aurora-1-5-extending-open-foundation-models-for-weather-and-earth-system-applications/
title: Aurora 1.5: Extending open foundation models for weather and Earth-system applications
site: microsoft-research
date: 2026-07-09
scraped_at: 2026-09-04T13:21:50+00:00
---

Published

By

Share this page

Aurora 1.5 is a major update to the open Aurora Earth-system foundation model, adding 22 new weather variables for a broader view of atmospheric conditions, hourly forecasts, and probabilistic ensemble forecasting. Developed by Microsoft Weather as an extension of the original model from Microsoft Research AI for Science, Aurora 1.5 shows how frontier research can move into broader use: open for researchers and developers to evaluate and extend, and designed to support customers where additional data, infrastructure, and operational assurance is needed. As climate and weather-related risks continue to affect communities, infrastructure, and economies worldwide, advances in Earth-system forecasting can help improve preparedness and decision-making.

Aurora is a foundation model for the Earth system developed by Microsoft Research AI for Science, first introduced in 2024 and

in 2025. It showed that a single model could be adapted to medium-range weather, ocean waves, atmospheric chemistry, and emerging climate applications, including high-resolution weather forecasting through fine-tuning. Its growing use has reinforced the value of an open, collaborative model that is easier to adapt, evaluate, and put to use.

This

builds on that foundation by making the model openly available for the global community to adapt, extend, and build on.

Aurora 1.5 advances the broader effort to make open weather foundation models practical and scalable for organizations that rely on atmospheric and Earth-system intelligence. Alongside new variables and higher temporal resolution, Aurora 1.5 adds one of the most requested capabilities from users: ensemble forecasting. Because forecasts are sensitive to initial conditions and model uncertainty, ensembles run multiple simulations to show the range and likelihood of possible outcomes. Aurora 1.5 builds on Microsoft Research’s scientific foundation with new product engineering, cloud infrastructure, managed access, and decision-support capabilities. Together, these advances make Aurora 1.5 a valuable enterprise-grade weather solution for organizations.

The breadth update adds 22 new variables to Aurora’s original 4, including representative surface, pressure-level, wind, temperature, humidity, precipitation, and radiation fields. That broader coverage makes the model more relevant for sectors that depend on integrated Earth-system signals, from energy and agriculture to transport and resilience planning.

The update to hourly temporal resolution enables fine-grained detail for precision operational guidance, such as the onset of precipitation, trade decisions, or a landfalling tropical cyclone.

Join us for a continuous exchange of ideas about research in the era of general AI. Watch the latest episodes on demand.

The ensemble version of Aurora 1.5 introduces stochastic perturbations to represent model uncertainty, allowing the generation of multiple forecast members to estimate the spread of possible futures. For a multitude of applications including power systems, transport, agriculture, extreme-weather planning, and climate risk, the model distribution matters as much as the best estimate.

This ensemble capability was developed through multi-stage fine-tuning on top of the original Aurora model. After expanding the variable set and adding hourly temporal resolution, the team introduced controlled perturbations into the model’s latent conditioning pathway and optimized the ensemble for probabilistic forecast quality. A final round of auto-regressive fine-tuning on ECMWF High Resolution (HRES) analysis data from 2018 to 2023 improved rollout behavior and stability.

Aurora’s ensemble approach summarizes uncertainty across multiple model runs. Its probabilistic forecasts outperform those of the state-of-the-art ECWMF dynamical ensemble on 88.9% of evaluated targets (Figure 1). In evaluations on all 2024–2025 tropical cyclones, Aurora 1.5 substantially reduced track errors, including roughly one-third lower track error when comparing the ensemble median to the original Aurora. An example for the devastating Hurricane Helene shows how Aurora 1.5’s skill translates to high-impact weather applications.

Beyond medium-range weather applications, Terradot – part of the Microsoft Climate Innovation Fund portfolio—is working with the

and the Microsoft Research Accelerator on

to estimate and optimize carbon dioxide removal from enhanced rock weathering under real field conditions. Sasankh Munukutla, Co-Founder of Terradot, highlights

This work shows how Earth-system foundation models can support climate mitigation and public-interest science beyond forecasting, including settings where rigorous evaluation and responsible deployment matter.

Aurora is also being explored with partners such as the UK Met Office, exploring how foundation models can work alongside established physics-based systems to tackle problems from weather to climate time scales. The aim is faster, more flexible forecasts that support decision-making without replacing the science behind trusted prediction.

Microsoft connects open research, product engineering, responsible deployment, and partner ecosystems so that models can move from scientific advance to evaluated operational use. As an example, Aurora began in Microsoft Research AI for Science and is now being built on for operational use by Microsoft Weather, with AI for Good helping to evaluate public-interest applications. The platform path brings

, alongside Agent skills and Azure services that connect models with geospatial data, scalable infrastructure, and applied workflows.

: the company is using Aurora 1.5 alongside existing operational Microsoft Weather models to support energy operations where weather-dependent generation, infrastructure planning, and environmental data need to come together.

Aurora’s open-source availability is intended to help researchers, agencies, companies, and civil society evaluate, apply, and extend the model. Microsoft Weather is building on that open foundation to deliver easier access to Aurora forecasts through managed services, integrations, and responsible deployment paths for organizations that depend on weather and Earth-system intelligence.

Foundation models should complement—not replace—physics-based models and domain expertise. The opportunity is to use them responsibly, with careful evaluation and transparency, and to invite researchers, agencies, companies, and public-interest partners to test where Aurora and related Microsoft Weather capabilities can improve forecasting, planning, and climate resilience in their own settings.

Microsoft Weather is the AI-based forecasting team behind weather experiences across Windows, Bing, Copilot, Edge, and MSN, reaching more than a billion devices across 180 countries. The team has been applying AI to operational weather forecasting for more than seven years and has built a proven track record of delivering high-quality forecasts at global scale. Microsoft Weather has won multiple forecasting competitions and was ranked the world’s most accurate global forecast provider by an independent third party for three consecutive years from 2022 to 2024. Building on today’s Aurora 1.5 announcement, the team plans to extend this work in the coming months with additional fit-for-purpose AI weather models designed for enterprise scenarios where forecast quality, speed, uncertainty, and operational decision support matter most.

If you are interested in exploring Aurora and Microsoft Weather solutions for commercial or organizational applications, please contact us at

Director, Research Incubations

Principal Applied Science Manager

Applied Scientist

Principal Data and Applied Scientist

Senior Product Manager

Sr. Director Data Science

Creative Technologist

Corporate Vice President & Chief Data Scientist

Corporate Vice President and Managing Director, Microsoft Research Accelerator

Managing Director, Microsoft Research AI for Science
