import queue
import threading
import time


def go(i, end,  q):
  def run(a, b):
    for j in range(a, b):
      if not q.empty():
        pair = q.get()
        pair[1].join()
        run(pair[0], b)
        break
      print("i: " + str(i) + " j: " + str(j))
      time.sleep(.1)
  run(0, end)

def test():
  k = queue.Queue()
  l = queue.Queue()
  t1 = threading.Thread(target=go, args=[0, 600, k])
  t2 = threading.Thread(target=go, args=[1, 200, l])
  print("Start")
  t1.start()
  time.sleep(15)
  print("Interrupt")
  k.put((200, t2))
  t2.start()
  t2.join()
  print("End 2")
  t1.join()
  print("End 1")



