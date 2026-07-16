val = 0


def action1(val, callbacks=[]):
  print('before', val)
  val += val
  print('after', val)
  while len(callbacks) > 0:
    callback = callbacks.pop()
    if callable(callback):
      scrmsg = 'entered callable and calling with val = {val} & callback = {callback}'.format(val=val, callback=callback)
      print(scrmsg)
      val += callback(val, callbacks)
  return val


def action2(val, any):
  print('in action2', val)
  return val


callbacks = [
  action1, action2
]
print(callbacks)


newval = action1(5, callbacks)
print('end', newval)

