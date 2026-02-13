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
