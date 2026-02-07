export async function fetchSummary(apiUrl) {
  const [templates, instances, profiles] = await Promise.all([
    fetch(`${apiUrl}/emulators/templates`).then((res) => res.json()),
    fetch(`${apiUrl}/emulators/instances`).then((res) => res.json()),
    fetch(`${apiUrl}/profiles`).then((res) => res.json()),
  ])

  return {
    templates: templates.length || 0,
    instances: instances.length || 0,
    profiles: profiles.items?.length || 0,
  }
}
