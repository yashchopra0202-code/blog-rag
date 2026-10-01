---
url: https://deepmind.google/blog/introducing-synthid-bio/
title: Introducing SynthID Bio
site: deepmind
date: 2026-09-30
scraped_at: 2026-10-01T10:35:47+00:00
---

Pushmeet Kohli, David Stutz, Ali Cowen-Rivers and Jeremy Ratcliff

Proof of concept for watermarking AI-generated proteins while preserving biological function.

Today, we’re introducing SynthID Bio to bring watermarking technology to synthetic biology. SynthID Bio embeds an imperceptible signature directly into the biological code, ensuring the watermark is verifiable not just on a digital model but on the synthesized, physical protein itself – all while preserving its biological function in laboratory testing.

Generative AI is helping scientists address critical biological challenges, from predicting the structure of proteins (

) to designing entirely new proteins (

, and

), and more recently, developing new

, viruses that infect bacteria. Yet these tools also present new challenges: novel AI designs can bypass traditional DNA synthesis screening, while mislabeled synthetic 3D structures risk polluting public databases and misleading downstream research.

SynthID Bio is a family of watermarking methods developed specifically for synthetic biology to strengthen biosecurity and scientific integrity.

It adapts its approach depending on the type of data, subtly guiding the choice of amino acids for sequences and adjusting atomic coordinates for predicted 3D structures, creating a reliable signal for detection.

In experiments, these adjustments did not compromise the protein’s biological function, which is essential to effectively treat disease and advance scientific research.

Visualization of the predicted structure of our watermarked VEGF-A protein binder with watermark signal indicated by color for each amino acid.

We verified our approach for watermarking protein binders, i.e. molecules built to selectively latch onto other proteins, by using our binder design method AlphaProteo alongside a SynthID Bio-enabled version of ProteinMPNN, the commonly used protein sequence generation method.

In wet-lab testing across three target proteins (VEGF-A, the SARS-CoV-2 spike protein RBD, and PD-L1), our watermarked designs matched the hit rate, binding affinity, and natural sequence diversity of unwatermarked versions, successfully creating the first-ever watermarked and biologically functional protein binders.

Binding affinity, measured as KD, comparing non-watermarked and watermarked protein designs across three targets. Lower indicates stronger binders.

For protein folding, SynthID Bio fine-tunes a small part of AlphaFold 3’s diffusion network, building the ability to watermark directly into the model’s weights. This ensures that the predicted 3D coordinates inherently carry a detectable signature regardless of who runs the model. SynthID Bio preserves AlphaFold 3 prediction accuracy while offering near-perfect detectability, maintaining key structural feature distributions, and holding up against digital noise or minor coordinate changes.

On 7PPA, we show the AF3 predicted structure (left), the ground truth structure (middle), and the watermarked structure (right).

Biosecurity relies on layered defenses – think of it like a “Swiss cheese” defense model, where multiple independent safety measures work in tandem to cover each other’s blind spots. Safeguards like model-level mitigations and customer vetting each represent critical layers with potential gaps. As a part of our broader

, SynthID Bio’s watermarking approach serves as an important, tangible verification layer embedded in the biological design itself.

That layer is especially vital to DNA synthesis screening, which sits on the frontlines of biosecurity. Converting digital protein designs into physical molecules requires placing an order with DNA synthesis providers, who screen requests against databases of known threats. For example, historically, an unfamiliar sequence may have been safely assumed to be an undiscovered natural organism. But because AI can create

screeners can no longer make that assumption. Verifying that an unfamiliar order isn't an engineered threat requires exhaustive manual reviews that can stall vital research. Here, SynthID Bio can provide an automated verification signal, proving an order originated from a trusted model with built-in safeguards.

Similarly, SynthID Bio could help maintain the integrity of databases such as the Protein Data Bank, UniProt, and GenBank. These databases, many of which are open to public submission, play a vital role in scientific advancements – but mislabeled entries can have an

, a challenge that may only grow with the addition of AI-generated biological data. As a part of the submission process, SynthID Bio could help ensure synthetic entries are properly labeled or flagged for further review.

While no single biosecurity intervention is a silver bullet, SynthID Bio brings

, our tried and tested watermarking tool, to synthetic biology. It’s an important first step toward reliably identifying and tracking AI-generated biological sequences and structures.

Moving forward, key challenges include making the watermark more robust against deliberate tampering. SynthID Bio can also be paired with provenance

approaches – similar to

for digital media – or

to better identify and track AI-generated proteins.

To match the growing capabilities of frontier AI technology, we’re also researching how to apply watermarking to more complex biological objects. In ongoing work with the

at Stanford University and Arc Institute, we integrated SynthID Bio into Evo 2, an advanced genomic model, to watermark the genome of an

. Early laboratory testing in bacteria cultures has confirmed these watermarked bacteriophages are functional. We believe this work has the potential to address some of the

associated with genome design and will share more details in a technical manuscript soon.

Realizing the full biosecurity benefits of this work will require community collaboration and further research. As part of our commitment to responsible innovation, we are publishing our

and open-sourcing the code and

data, and releasing the weights to the research community, so we can build on this work. By working openly with partners across biosecurity, gene synthesis, and policy, we can ensure safety and responsibility keeps pace with AI-driven discovery.

This project was initiated by Pushmeet Kohli. The research and technical development was led by Alexander I. Cowen-Rivers and David Stutz and was advised by Pushmeet Kohli. Key engineering and research contributions were made by Guillermo Ortiz-Jimenez, Jeremy Ratcliff, Vinicius Zambaldi, Lindsay Willmore, Josh Abramson, Harshnira Patani, Christina Kouridi, Florian Stimberg, Mel Vecerik, Alex Chu, Sukhdeep Singh, Sumanth Dathathri, Eliseo Papa, Valentin De Bortoli, Arnaud Doucet, Jue Wang, and Sven Gowal. We thank

for help with

validation.

The extension of this work to watermark DNA of bacteriophages is a collaboration between Google DeepMind and the Hie lab at Stanford and Arc Institute with key contributions from Jeremy Ratcliff, Aleks Petrov, Alexander I. Cowen-Rivers, David Stutz, Elisa L. H. Wong, Victor Martin Palacios, Francesca Pietra, Alfred Piccioni, Tristan Oliver Kwan, Tor Lattimore, Sumanth Dathathri, and Pushmeet Kohli from Google DeepMind and Brian Hie, Samuel King, and Aditi Merchant from Arc Institute and Stanford.

We further thank Rudy Bunel, Anna Cupani, Rob Fergus, Thomas Frerix, Sahra Ghalebikesabi, John Jumper, Jacob Kelly, David La, Victor Martin, Sebastian Nowozin, Stig Petersen, Aleks Petrov, Uchechi Okereke, Sylvestre-Alvise Rebuffi, Rosalia Schneider, Armin Senoner, Richard Shuai, Ashok Thillaisundaram, Elisa L. H. Wong, Zachary Wu, and Augustin Žídek for their contributions to the research article, and Julien Bergeron for contributions to the 3D rendering. Finally, we thank Demis Hassabis for his encouragement and support of this project.
