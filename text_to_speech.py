import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cpu")

text = "In computer science, a linked list is a linear data structure where elements are stored in nodes, and each node points to the next one in the sequence. Unlike arrays, linked lists do not require contiguous memory, making them efficient for inserting or deleting elements without shifting others. There are different types of linked lists, such as singly linked lists, doubly linked lists, and circular linked lists. They are important because they provide dynamic memory allocation and allow for flexible data management, especially in cases where the size of the data set changes frequently"
wav = model.generate(text)
ta.save("test-1.wav", wav, model.sr)


