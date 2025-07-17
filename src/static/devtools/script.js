const output = document.getElementById('output');
const baseUrl = `${window.location.origin}/api/v1/contacts`;

function getSchemaHeader() {
  const schema = document.getElementById('schemaInput').value.trim();
  return { 'X-SCHEMA': schema || 'public' }; // default fallback
}

// GET contacts
async function apiGet() {
  output.textContent = 'Loading GET...';
  try {
        const res = await fetch(baseUrl, {
        method: 'GET',
        headers: getSchemaHeader()
      });
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = 'GET error: ' + err;
  }
}

// POST (create contact)
document.getElementById('createForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = e.target;
  const payload = {
    name: form.name.value,
    email: form.email.value,
    phone: form.phone.value || null
  };

  output.textContent = 'Creating contact...';

  try {
    const res = await fetch(baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getSchemaHeader()
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    output.textContent = res.status === 201
      ? 'Created:\n' + JSON.stringify(data, null, 2)
      : 'POST error: ' + JSON.stringify(data);
  } catch (err) {
    output.textContent = 'POST error: ' + err;
  }
});

// PUT (update contact)
document.getElementById('updateForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const form = e.target;
  const contactId = form.id.value;
  const payload = {
    name: form.name.value,
    email: form.email.value,
    phone: form.phone.value || null
  };

  output.textContent = 'Updating contact...';

  try {
    const res = await fetch(`${baseUrl}/${contactId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getSchemaHeader()
      },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    output.textContent = 'PUT error: ' + err;
  }
});

// DELETE contact
async function apiDelete() {
  const contactId = document.getElementById('deleteId').value;
  if (!contactId) {
    output.textContent = 'Please enter a contact ID to delete.';
    return;
  }

  output.textContent = 'Deleting contact...';

  try {
    const res = await fetch(`${baseUrl}/${contactId}`, {
      method: 'DELETE',
      headers: getSchemaHeader()
    });
    output.textContent = res.status === 204
      ? `Contact ${contactId} deleted successfully (204).`
      : 'DELETE error: ' + await res.text();
  } catch (err) {
    output.textContent = 'DELETE error: ' + err;
  }
}
