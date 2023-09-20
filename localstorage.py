import streamlit as st
import streamlit.components.v1 as components

localstorage = components.declare_component("localstorage", path="localstorage")

def save_data(key: str, value: str):
    return localstorage(command="save", key=key, value=value)

def load_data(key: str, callback=None):
    response = localstorage(command="load", key=key)
    print("Received response from JavaScript:", response)
    if response and 'loadedData' in response:
        if callback:
            callback(response['loadedData'])
        return response['loadedData']
    else:
        return None

def clear_storage():
    return localstorage(command="clear")

def remove_data_by_key(key: str):
    return localstorage(command="remove", key=key)
