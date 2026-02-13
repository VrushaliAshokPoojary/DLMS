function buildHeaders(apiKey) {
  if (!apiKey) {
    return undefined
  }
  return {
    'X-API-Key': apiKey,
  }
}

export async function fetchSummary(apiUrl, apiKey) {
  const headers = buildHeaders(apiKey)
  const [templates, instances, profiles] = await Promise.all([
    fetch(`${apiUrl}/emulators/templates`, { headers }).then((res) => res.json()),
    fetch(`${apiUrl}/emulators/instances`, { headers }).then((res) => res.json()),
    fetch(`${apiUrl}/profiles`, { headers }).then((res) => res.json()),
  ])

  return {
    templates: templates.length || 0,
    instances: instances.length || 0,
    profiles: profiles.items?.length || 0,
  }
}

export async function listTemplates(apiUrl, apiKey) {
  return fetch(`${apiUrl}/emulators/templates`, { headers: buildHeaders(apiKey) }).then(toJson)
}

export async function createInstance(apiUrl, apiKey, payload) {
  const params = new URLSearchParams(payload)
  return fetch(`${apiUrl}/emulators/instances?${params.toString()}`, {
    method: 'POST',
    headers: buildHeaders(apiKey),
  }).then(toJson)
}

export async function runWorkflow(apiUrl, apiKey, meterId) {
  const headers = buildHeaders(apiKey)
  const [fingerprint, profile, association, objects, obis, vendor] = await Promise.all([
    fetch(`${apiUrl}/fingerprints/${meterId}`, { method: 'POST', headers }).then(toJson),
    fetch(`${apiUrl}/profiles/${meterId}`, { method: 'POST', headers }).then(toJson),
    fetch(`${apiUrl}/associations/${meterId}`, { method: 'POST', headers }).then(toJson),
    fetch(`${apiUrl}/associations/objects/${meterId}`, { headers }).then(toJson),
    fetch(`${apiUrl}/obis/normalize/${meterId}`, { headers }).then(toJson),
    fetch(`${apiUrl}/vendors/classify/${meterId}`, { headers }).then(toJson),
  ])

  return { fingerprint, profile, association, objects, obis, vendor }
}
