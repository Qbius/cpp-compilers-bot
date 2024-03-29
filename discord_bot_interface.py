import pickle
import os

anonymous_object = lambda: type('', (), {})()

def create_state(**kwargs):
    obj = anonymous_object()
    obj.__dict__ = kwargs
    return obj

def load_state():
    obj = anonymous_object()
    obj.__dict__ = pickle.load(open('state.info', 'rb'))
    return obj

def save_state(obj):
    pickle.dump(obj.__dict__, open('state.info', 'wb'))

def check_if_last_arguments(fun, args):
    fun_params = list(signature(fun).parameters)
    kwarg_params = [k for k in fun_params if k in ['message', 'state']]
    return set(kwarg_params) - set(fun_params[-len(kwarg_params):])
    
import discord
import asyncio
from inspect import signature, Parameter, iscoroutine

client = discord.Client()
print('Initializing...')


class command(object):

    available_commands = dict()

    @staticmethod
    def add_command(prefix, fun):
        not_last_special_args = check_if_last_arguments(fun, ['message, state'])
        if len(not_last_special_args) > 0:
            raise SyntaxError(f"{fun.__name__} command: {', '.join(not_last_special_args)} not at the back of the argument list")
        else:
            command.available_commands[f'{prefix}{fun.__name__}'] = fun
            print(f"Added command {fun.__name__}")

    def __init__(self, fun):
        command.add_command('!', fun)

    @staticmethod
    def override_prefix(pref):
        return lambda fun: command.add_command(pref, fun)

    @staticmethod
    def call_command(msg):
        cmd_name, *args = msg.content.split(' ')
        if cmd_name not in command.available_commands: return
        cmd = command.available_commands[cmd_name]
        fun_params = signature(cmd).parameters
        kwargs = {k: v for k, v in {'message': msg, 'state': load_state()}.items() if k in fun_params}

        normal_args = [k for k in fun_params.keys() if k not in kwargs.keys()]
        if len(normal_args) != len(args):
            args_err_msg = f"Error, expected {len(normal_args)} arguments (got {len(args)})\nExpected arguments: "
            args_err_msg += ','.join([f'{arg_name}' + (f' (default: {fun_params.get(arg_name).default})' if fun_params.get(arg_name).default != Parameter.empty else '') for arg_name in normal_args])
            return args_err_msg
        else:
            res = cmd(*args, **kwargs)
            if 'state' in kwargs: save_state(kwargs['state'])
            return res

@client.event
async def on_message(msg):
    response = command.call_command(msg)
    if response: await msg.channel.send(response)

def event(fun):
    if check_if_last_arguments(fun, ['state']):
        raise SyntaxError("state needs to be the last argument")

    def inner(*a, **kw):
        kwargs = {k: v for k, v in {'state': load_state()}.items() if k in signature(fun).parameters}
        result = fun(*a, **{**kw, **kwargs})
        if 'state' in kwargs.keys(): save_state(kwargs['state'])
        return result

    return client.event(inner)

class task(object):
    @staticmethod
    def add_task(fun):
        client.loop.create_task(fun())
        print(f"Added task {fun.__name__}")

    def __init__(self, fun):
        task.add_task(fun)

    @staticmethod
    def loop(seconds):
        def decorate_loop(fun):
            if check_if_last_arguments(fun, ['state']):
                raise SyntaxError("state needs to be the last argument")

            inner = fun
            if 'state' in signature(fun).parameters:
                def state_inner():
                    state = load_state()
                    res = fun(state)
                    save_state(state)
                    return res
                inner = state_inner

            async def loop_task():
                await client.wait_until_ready()
                while not client.is_closed():
                    res = inner()
                    if iscoroutine(res): await res
                    elif isinstance(res, list): [await ele for ele in res]
                    else: pass
                    await asyncio.sleep(seconds)
            
            loop_task.__name__ = fun.__name__
            task.add_task(loop_task)
        return decorate_loop

def run(token = open('bot_token').read().strip(), default_state = anonymous_object()):
    if not os.path.exists('state.info'): save_state(default_state)
    client.run(token)