// POST /api/submit
// Receives every form on the site (join, guest, contact, details, newsletter)
// and stores it in the D1 database bound as DB. Nothing is emailed or shared.

const FORMS = {
  join: ["brand", "founder", "city", "makes", "instagram", "year", "why", "door", "email"],
  guest: ["guest_name", "guest_work", "why", "link", "name", "email"],
  contact: ["name", "email", "reason", "message"],
  details: ["name", "email", "answer"],
  newsletter: ["email"],
};
const OPTIONAL = {
  join: ["website", "phone", "declaration"],
  guest: [],
  contact: ["phone"],
  details: [],
  newsletter: [],
};
const MAX_FIELD = 2000;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function reply(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

export async function onRequestPost({ request, env }) {
  let input;
  try {
    const type = request.headers.get("content-type") || "";
    if (type.includes("application/json")) {
      input = await request.json();
    } else {
      input = Object.fromEntries(await request.formData());
    }
  } catch {
    return reply(400, { ok: false, error: "We could not read the form. Refresh the page and try again." });
  }

  // honeypot: real people never fill this hidden field
  if (input.company_website) return reply(200, { ok: true });

  const form = String(input.form || "");
  if (!FORMS[form]) return reply(400, { ok: false, error: "Unknown form." });

  if (input.consent !== true && input.consent !== "on" && input.consent !== "true") {
    return reply(400, { ok: false, error: "Tick the consent box so we can store your details." });
  }

  const data = {};
  for (const key of FORMS[form]) {
    const value = String(input[key] ?? "").trim();
    if (!value) return reply(400, { ok: false, error: `Fill in every required field. Missing: ${key.replace("_", " ")}.` });
    if (value.length > MAX_FIELD) return reply(400, { ok: false, error: "One of the answers is too long. Shorten it and try again." });
    data[key] = value;
  }
  for (const key of OPTIONAL[form]) {
    const value = String(input[key] ?? "").trim().slice(0, MAX_FIELD);
    if (value) data[key] = value;
  }
  if (!EMAIL_RE.test(data.email)) {
    return reply(400, { ok: false, error: "Enter an email address like name@example.com." });
  }

  const consentText = String(input.consent_text || "").slice(0, 500) || "consent given";
  try {
    await env.DB.prepare(
      "INSERT INTO submissions (form, name, email, data, consent_text) VALUES (?1, ?2, ?3, ?4, ?5)"
    ).bind(form, data.name || data.founder || null, data.email, JSON.stringify(data), consentText).run();
  } catch (err) {
    return reply(500, { ok: false, error: "Something went wrong on our side. Email zeroingindia@gmail.com and we will reply." });
  }
  return reply(200, { ok: true });
}

export function onRequest() {
  return reply(405, { ok: false, error: "Use POST." });
}
