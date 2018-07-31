This repo describes algorithmically the Online Context Language Model (OCLM) model. The paper [A Multi-Context Character Prediction Model for a Brain-Computer Interface](http://aclweb.org/anthology/W18-1210) written by Dudy, Xu, Bedrick, and Smith provides further details to the priciples and motivation for this project in addition to a proof of concept.

The code in the repo was mainly written by Dudy and Xu.

Additional requirements to run the code are:
  * [openfst](http://www.openfst.org/twiki/bin/view/FST/WebHome)
  * openfst for python (pip install openfst)
  * compiled [ebitweight](https://github.com/shiranD/ebitweight)
  * compiled [specilizer](https://github.com/shiranD/specializer)
  * optional: requests and json for python
Or Alternatively, you can ask for the docker image as everything is found there and ready for the either train+test or just test (with the current trained model)
