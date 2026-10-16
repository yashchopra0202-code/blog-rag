---
url: https://deepmind.google/blog/accelerating-antimicrobial-discovery/
title: Accelerating the search for antimicrobial peptides with Google Antigravity
site: deepmind
date: 2026-10-15
scraped_at: 2026-10-16T08:37:54+00:00
---

Pengfei Tian, Maxwell L. Bileschi, Zoi Tsangalidou, Sukhdeep Singh and Lucy J. Colwell

New antibiotics are urgently needed to help with rising levels of antimicrobial resistance, but searching for new therapeutics is often a slow, labor-intensive process. With Google Antigravity, our agentic development platform, this process can now be made easier.

Google Antigravity provides an agentic science workbench that empowers biologists to discover, structurally evaluate, and prioritize promising targets quickly, compressing what used to be a fragmented search over multiple databases into a single session. It also helps researchers scan through millions of previously uncharacterized proteins in the UniProt database using ProtNLM, a model that predicts biological function from amino acid sequences.

This technical walkthrough shows how biologists used Google Antigravity to uncover a novel antimicrobial peptide candidate which has predicted activity against the pathogens involved in respiratory tract infections. The lead identified here is now undergoing wet-lab validation.

Rising

is one of the most pressing global health crises of our time and could result in an estimated 10 million annual deaths globally by 2050. To prevent this, we urgently need to discover novel therapeutics. Antimicrobial peptides (AMPs), particularly bacteriocins, offer a promising alternative to traditional antibiotics because they have naturally evolved to target fundamental vulnerabilities in competing bacteria, from cell envelopes to essential intracellular machinery, making it difficult for pathogens to develop resistance.

The exponential growth of genomic and metagenomic sequencing has populated global databases with billions of natural amino acid sequences. This pool of natural data has already produced globally used bacteriocins like Nisin, alongside recent genome-mined breakthroughs such as Darobactin, Dynobactin, and Lariocidin.

Many, however, remain locked within the unannotated "dark matter" of protein databases, with their function uncharacterized because they aren’t similar to known proteins. For example, the world's leading public resource of protein sequence and functional information,

, holds millions of sequences with unknown functionality, transferred directly from genome sequencing projects.

To bridge this gap, Google developed

, a deep learning model trained to directly read the underlying evolutionary “grammar” of amino acid sequences. This allows the model to predict biological function directly from raw protein sequences, enriching millions of previously unnamed UniProt entries with high-confidence functional labels.

Overview of the ProtNLM pipeline translating raw amino acid sequences into natural-language biological annotations for unreviewed UniProtKB/TrEMBL entries. The functional annotation scope of the system covers protein names, function comments, subcellular locations, and GO terms, in addition to keywords.

Scientific discovery is rarely a single step process; finding viable candidate proteins requires human intuition and iteration to incorporate new empirical evidence. Working in Antigravity, the researcher and AI agent begin by setting a focused biological goal: find and computationally validate novel AMPs in

. During an interactive, multi-turn session the researcher steers the scientific strategy, deciding which questions to ask and what evidence to collect, while the agent handles the heavy lifting of cross-database orchestration, structural analysis, and literature synthesis.

The agent queries the database and filters millions of entries down to a handful of candidates worthy of attention. Here, the agent finds a bacteriocin (Uniprot ID:

) with a length of 97 amino acids from the Lactococcin 972 family.

To verify the novelty of this discovery, the researcher guides the agent to interrogate the candidate against curated knowledge in Swiss-Prot via the EMBL-EBI NCBI-BLAST service and confirm this peptide has no meaningful sequence homolog among manually reviewed proteins.

The researcher steers the analysis towards structural evidence. The agent retrieves the candidate’s 3D model from the

querying it against experimentally determined structures to identify remote homologs, and superimposing the models to assess similarity. Here, the structural evidence corroborates ProtNLM’s prediction by showing the candidate's fold closely matches an experimentally determined bacteriocin. The structure viewer in Antigravity allows this structural analysis to be seamlessly performed in one place.

The agent looks beyond the molecule itself to its genomic neighborhood, reasoning over whether the surrounding machinery supports the AMP hypothesis. Inspecting the flanking genes, it spots a revealing pattern: our previously uncharacterized candidate sits at the upstream of a tightly coupled operon, just 6 base pairs ahead of a ABC transporter permease and its potential partner ATP-binding protein, alongside another annotated bacteriocin and an XRE transcriptional regulator. This provides strong contextual evidence that it is part of a working bacteriocin system.

By reviewing the existing literature, the agent proposes how the molecule might act and what pathogens it might act on. In this case, existing evidence suggests a mechanism of action targeting bacterial cell division, and a predicted potency spectrum spanning several drug-resistant pathogens.

Finally, the agent translates its in silico findings into an actionable bench protocol, spanning protein expression, antimicrobial susceptibility testing, target engagement, and in vitro toxicity testing, bridging the gap from computational prediction to wet-lab experiment. This step is already in motion: this candidate - along with several others discovered through the same pipeline - are now in wet-lab validation, where experimental results will provide the ultimate test of the agent's analysis.

The candidate we uncover in this walkthrough represents a biologically plausible lead backed by structural and genomic evidence but it still requires wet lab validation. What makes this meaningful is how dramatically it lowers the barrier to everyday biological workflows, turning days of fragmented database triage into a single collaborative session. While this session focused on a narrow amino acid window in

, researchers can take the conversation in any direction, such as layering in new filtering criteria, exploring different sequence lengths, or targeting other priority pathogens. By broadening the search from human commensals to environmental microbes and beyond, scientists can guide the agent across UniProt to discover novel AMP candidates at scale.

A protein's 3D structure can help us understand its biological function. Examining a candidate’s predicted fold in space is key. To provide this end-to-end workflow in a single workspace, we are introducing the

, a 3D visualization tool embedded directly into Antigravity.

The researcher and agent work together over a shared visual state. As the agent retrieves structures from AlphaFold Database or the scientist’s own predictions, it can dynamically drive the viewer. For instance, it can highlight key functional regions to visually explain its hypotheses. Crucially, this awareness flows both ways: actions like highlighting specific residues or pinning notes directly onto a binding pocket are synchronised back to the agent. A researcher can simply mark a region of interest in 3D space and ask, for example, "How might this β-strand affect Lipid II binding?", allowing the agent to immediately reason over the exact structural context the scientist is looking at.

The Biomolecular Structure Viewer inside Antigravity showing the AlphaFold-predicted structure of the candidate bacteriocin, giving the researcher and agent a shared 3D canvas to inspect and annotate functional regions.

Historically, uncovering insights like those in the workflow demonstrated above required fragmented and specialised software: writing custom scripts to query databases, manually exporting files to 3D modelling programs, managing disconnected genomic tools and working with multiple experts to design the wet lab assays. Because wet-lab validation remains resource-intensive, narrowing the search space to only the highest-confidence leads upfront is critical. Using Google Antigravity allows researchers to navigate the vast biological search space efficiently while leveraging accurate protein function predictions from a domain-specific model.

Google Antigravity executes this end-to-end scientific reasoning in one place. This allows scientists to spend more time evaluating high-quality hypotheses, running experiments in the lab and solving research challenges.

We would like to acknowledge the contributions of the following team members: Maria Gabriela Cardoso, Victoria Johnston, Lexi Walker, Gena Hong, James King, Richard Green, Filip Radlinski, Artem Sobolev, Michael V. LeVine, Ruijie K. Zhang, Zachary Wu, Luca Schulz, Amy Danson, Tristan Oliver Kwan, Ryan Krueger, Oleg Kovalevskiy, Doug Fritz, Yunhan Xu, Sebastian Nowozin
