# DynReconfig

Tailoring the machine hardware to varying needs of the software running on top of it 
is crucial to achieving energy-efficient execution. However, the characteristics of the code
are non-deterministic and depend on system environments, precluding the use of static 
methods for tuning the hardware to match the requirements. We propose the use of machine 
learning models which can be trained to suggest energy-optimal hardware configurations, given
a previously unseen application. We evaluate our model using application traces from an x86 
simulator, and measure the closeness of the predicted hardware configuration to the one achieving 
the best energy-efficiency for the application. The machine learning model is trained using Google 
TensorFlow.
