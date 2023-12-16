'use client'

function storageAvailable (type) {
  // https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API
  let storage
  try {
    storage = window[type]
    const x = '__storage_test__'
    storage.setItem(x, x)
    storage.removeItem(x)
    return true
  } catch (e) {
    return (
      e instanceof DOMException &&
            // everything except Firefox
            (e.code === 22 ||
                // Firefox
                e.code === 1014 ||
                // test name field too, because code might not be present
                // everything except Firefox
                e.name === 'QuotaExceededError' ||
                // Firefox
                e.name === 'NS_ERROR_DOM_QUOTA_REACHED') &&
            // acknowledge QuotaExceededError only if there's something already stored
            storage &&
            storage.length !== 0
    )
  }
}

const storage = storageAvailable('localStorage')
  ? window.localStorage
  : storageAvailable('sessionStorage') ? window.sessionStorage : null

export function setStorage (key, value) {
  if (storage) {
    storage.setItem(key, JSON.stringify(value))
  }
}

export function getStorage (key, defaultValue = null) {
  if (storage) {
    const value = storage.getItem(key)
    return value ? JSON.parse(value) : defaultValue
  }
  return defaultValue
}

export function delStorage (key) {
  if (storage) {
    storage.removeItem(key)
  }
}
