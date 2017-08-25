import oauth2
#1) stream_2017_rice_research_3
consumer1 = oauth2.Consumer(key="DTuoGABTnFlDoYAXyF3EMOkHt", secret="nzfvURfghCOPwvl4J5IVOR3GNoyhJXEJNxDhy7seLclnTnlkKV")
token1 = oauth2.Token(key="1979279791-lryQcPzr1iru4UxF3USWKpexLYW38qcxhTFdnfZ", secret="xZjeY4hUsaAYpE2MkdPFqmJhFvUzFxCjMaMKg9rgX86z7")

#2)from Joe Chen
consumer2 = oauth2.Consumer(key="CuyDAqUbCTF6y6k6mcoGF8owZ", secret="OucJJMnHbYCVNKNgyEJSNBMWBXapwSGuwy1Xc28mXR5vLixrNQ")
token2 = oauth2.Token(key="1979279791-8qRguXNd21mgHR8khU9hg8rcyXkHHSE65tkwFlv", secret="HIR4DQEyHVPrvXm2XNsTToVcgIgxWM2WR2eOoaY1iJV6R")

#3)from Joe Chen, another one
consumer3 = oauth2.Consumer(key="z4k1E4pOj8ncQ4MAdjY1r1Ty9", secret="92mLHrYChG5sHRdZsUc90JG7RRh8cewrl5Hjf2IoPunCAL8HRz")
token3 = oauth2.Token(key="1979279791-tSDamC8WUIxU9Z8uFnkWe5eLNSUlGYhGu8l5zZ1", secret="FNMSlsqgcIRmjeCf0BqD9TamwAD1ZfMC77n0x0cOpsICZ")

#4) name: summer research project
#resource https://dev.twitter.com/rest/reference/get/statuses/user_timeline 
consumer4 = oauth2.Consumer(key="Vsj9hKjxGPk4JxBj4al3i7JHX", secret="TbPwe5ltq7U4GtaeMtUhyMxxYb6jNvgyXWZsGsjKqcxbZCFhbD")
token4 = oauth2.Token(key="1979279791-c9yR5GJlLrg78jTIifIckvllZf8NBRl8K5aU8OZ", secret="FHuPvdPcbU3Xu77I44pqc64FmLGh82Bkftgq0xwqmRHhR")

#5) stream_2017_rice_research
consumer5 = oauth2.Consumer(key="Kx4Qm05mBRI6Gznx7utPoI4hg", secret="RMRe3oN5Ks2LaoGULaQCMQjRw8l0iQ7FkYPPCdJRylJwyzpSyq")
token5 = oauth2.Token(key="1979279791-xiCAC2SGmQamAuFuG4CsSaVrFzF2848LgK1FHF7", secret="CwIGJKPk3v95aZCapbKQhyFgSl3XbfHIC2dgO7X6S0WnA")

#6) stream_2017_rice_research_2
consumer6 = oauth2.Consumer(key="mtn5SFSU5nSefxi0NTU0cuHDv", secret="IAIi3RraqvDlKoSadZ08N13SAaL7SXNz7As97f85VgOVIJg3mZ")
token6 = oauth2.Token(key="1979279791-xVMRTM2e8cPUFwmUeg8pYX5bPvznW9WPqyjIMbS", secret="kuIIo3pwpHNh9tFzJwE63CF9lL0lKRdlTVeUVxTIKjdzv")

#7) version2_2
consumer7 = oauth2.Consumer(key="BkzUSqw8Odz3PfK7GOhzLqxY0", secret="LRqiunkDEgBgRsYy8NV0l4BpyoOZT37y9lHuc51WxwtB4QfKMu")
token7 = oauth2.Token(key="1979279791-bz66kMYt28h9Kbrlhr1GIFiFkyUKEr1lqoXYix2", secret="tM2bV8m73oMJig7GmUwEPRyUpC09xw5ZQDELI3YlQ4RIO")

#8) version2_3
consumer8 = oauth2.Consumer(key="bJ2YoqBL7TQwbq0M0IxNoOuwO", secret="iRL9F1nrGX8CE4ivjMW7AVsDugDFj6PszLi3NyDVE64MKAbFNC")
token8 = oauth2.Token(key="1979279791-vdibNWYKuk2BTAn76rapNYtM1GdwpmqBxdQ6ml6", secret="A8qukDTSkZvc7yYCHf2isVzpkbvdBpxo9mHYX8qqqJmYX")

#9) name: streaming api bot detection
consumer9 = oauth2.Consumer(key="Nc5XxItLtpHBzJ7zTVIw0DMRf", secret="Bmr5NjiYWUiTs3eVtyG7yNL2S8XptnGUtvSWNw0RejfPVP7y6A")
token9 = oauth2.Token(key="1979279791-9X79gO6FsKqkIBK2ct73h101GZZgyTyEpWkLd09", secret="kT5JdOeybgmScy74qeDU2a3OBywvJJ0bGAfF72IDHHZJc")

#10) name: streaming api bot detection2
consumer10 = oauth2.Consumer(key="mrJtsTABCL8bhCiST3oF0xYuN", secret="dan23zYDbXc9oIGjXAMU3WbyKqeqYdRj4pWIG0So9fvqhTsuGi")
token10 = oauth2.Token(key="1979279791-aJUxu8Rd2SK3X7XFxcjN14gyL75x1ZQpSfoV6H8", secret="oUf9AdomderMawIi5td3d2sRr6MSpvI27mSdKsTvwZAUj")

def tokenpool():
	return [(consumer1, token1), (consumer2, token2), (consumer3, token3), (consumer4, token4), 
(consumer5, token5), (consumer6, token6), (consumer7, token7), (consumer8, token8), (consumer9, token9), (consumer10, token10)]
