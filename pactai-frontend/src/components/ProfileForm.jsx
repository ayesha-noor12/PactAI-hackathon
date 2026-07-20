import { useState } from 'react'

const CURRENCIES = ['USD', 'PKR', 'EUR', 'GBP', 'INR', 'AED']
const PROJECT_TYPES = ['Web Application', 'Mobile App', 'E-commerce', 'AI / ML', 'Portfolio / Branding', 'API / Backend']
const PLATFORMS = ['Web', 'Android', 'iOS', 'Desktop']
const DEFAULT_RANGES = {
  Web: { min: 200, max: 1000 },
  Android: { min: 300, max: 1500 },
  iOS: { min: 300, max: 1500 },
  Desktop: { min: 250, max: 1200 },
}

export default function ProfileForm({ initial, onSubmit, submitLabel = 'Save' }) {
  const [form, setForm] = useState({
    name: initial?.name || '',
    title: initial?.title || '',
    experience: initial?.experience ?? '',
    skills: initial?.skills?.join(', ') || '',
    hourly_rate: initial?.hourly_rate ?? '',
    working_hours_per_day: initial?.working_hours_per_day ?? '',
    minimum_profit_margin:
      initial?.minimum_profit_margin != null ? Math.round(initial.minimum_profit_margin * 100) : '',
    preferred_projects: initial?.preferred_projects || [],
    currency: initial?.currency || 'USD',
    pricing_mode: initial?.pricing_mode || 'hourly',
    platform_price_ranges: initial?.platform_price_ranges || DEFAULT_RANGES,
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function updateRange(platform, key, value) {
    setForm((f) => ({
      ...f,
      platform_price_ranges: {
        ...f.platform_price_ranges,
        [platform]: {
          ...(f.platform_price_ranges[platform] || DEFAULT_RANGES[platform]),
          [key]: Number(value),
        },
      },
    }))
  }

  function toggleProjectType(type) {
    setForm((f) => ({
      ...f,
      preferred_projects: f.preferred_projects.includes(type)
        ? f.preferred_projects.filter((t) => t !== type)
        : [...f.preferred_projects, type],
    }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await onSubmit({
        name: form.name,
        title: form.title,
        experience: Number(form.experience),
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
        hourly_rate: Number(form.hourly_rate),
        working_hours_per_day: Number(form.working_hours_per_day),
        minimum_profit_margin: Number(form.minimum_profit_margin) / 100,
        preferred_projects: form.preferred_projects,
        currency: form.currency,
        pricing_mode: form.pricing_mode,
        platform_price_ranges: form.platform_price_ranges,
      })
    } catch (err) {
      setError(err.message || 'Could not save your profile.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid sm:grid-cols-2 gap-5">
        <Field label="Full name">
          <input
            required
            value={form.name}
            onChange={(e) => update('name', e.target.value)}
            className={inputClass}
            placeholder="Ayesha Khan"
          />
        </Field>
        <Field label="Title">
          <input
            required
            value={form.title}
            onChange={(e) => update('title', e.target.value)}
            className={inputClass}
            placeholder="Full Stack Developer"
          />
        </Field>
      </div>

      <div className="grid sm:grid-cols-2 gap-5">
        <Field label="Experience" hint="Years">
          <input
            required
            type="number"
            min="0"
            value={form.experience}
            onChange={(e) => update('experience', e.target.value)}
            className={inputClass}
            placeholder="3"
          />
        </Field>
        <Field label="Skills" hint="Comma-separated">
          <input
            required
            value={form.skills}
            onChange={(e) => update('skills', e.target.value)}
            className={inputClass}
            placeholder="Python, FastAPI, React"
          />
        </Field>
      </div>

      <Field label="Currency">
        <select
          value={form.currency}
          onChange={(e) => update('currency', e.target.value)}
          className={`${inputClass} w-32`}
        >
          {CURRENCIES.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </Field>

      {/* Pricing mode toggle */}
      <div className="border border-paper-line rounded-lg p-4 bg-paper">
        <p className="text-xs font-medium text-ink/70 mb-3">How should PactAI price your projects?</p>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => update('pricing_mode', 'hourly')}
            className={`flex-1 px-3 py-2.5 rounded-md text-sm font-medium border transition-colors text-left ${
              form.pricing_mode === 'hourly'
                ? 'bg-brass/15 border-brass text-brass-dark'
                : 'bg-paper-card border-paper-line text-ink/60 hover:border-brass/40'
            }`}
          >
            Hourly rate
            <span className="block text-xs font-normal mt-0.5 opacity-70">
              Price = estimated hours × your rate
            </span>
          </button>
          <button
            type="button"
            onClick={() => update('pricing_mode', 'fixed_range')}
            className={`flex-1 px-3 py-2.5 rounded-md text-sm font-medium border transition-colors text-left ${
              form.pricing_mode === 'fixed_range'
                ? 'bg-brass/15 border-brass text-brass-dark'
                : 'bg-paper-card border-paper-line text-ink/60 hover:border-brass/40'
            }`}
          >
            Fixed range per platform
            <span className="block text-xs font-normal mt-0.5 opacity-70">
              You set a min–max per platform; complexity picks the price
            </span>
          </button>
        </div>
      </div>

      {form.pricing_mode === 'hourly' && (
        <div className="grid sm:grid-cols-3 gap-5">
          <Field label="Hourly rate">
            <input
              required
              type="number"
              min="0"
              value={form.hourly_rate}
              onChange={(e) => update('hourly_rate', e.target.value)}
              className={inputClass}
              placeholder="40"
            />
          </Field>
          <Field label="Working hours / day">
            <input
              required
              type="number"
              min="0"
              max="24"
              value={form.working_hours_per_day}
              onChange={(e) => update('working_hours_per_day', e.target.value)}
              className={inputClass}
              placeholder="8"
            />
          </Field>
          <Field label="Min. profit margin %">
            <input
              required
              type="number"
              min="0"
              max="100"
              value={form.minimum_profit_margin}
              onChange={(e) => update('minimum_profit_margin', e.target.value)}
              className={inputClass}
              placeholder="80"
            />
          </Field>
        </div>
      )}

      {form.pricing_mode === 'fixed_range' && (
        <div>
          <Field label="Price range per platform" hint={form.currency}>
            <div className="space-y-2">
              {PLATFORMS.map((platform) => {
                const range = form.platform_price_ranges[platform] || DEFAULT_RANGES[platform]
                return (
                  <div key={platform} className="flex items-center gap-3">
                    <span className="w-20 text-sm text-ink/70">{platform}</span>
                    <input
                      type="number"
                      min="0"
                      value={range.min}
                      onChange={(e) => updateRange(platform, 'min', e.target.value)}
                      className={`${inputClass} w-28`}
                      placeholder="min"
                    />
                    <span className="text-ink/40 text-sm">to</span>
                    <input
                      type="number"
                      min="0"
                      value={range.max}
                      onChange={(e) => updateRange(platform, 'max', e.target.value)}
                      className={`${inputClass} w-28`}
                      placeholder="max"
                    />
                  </div>
                )
              })}
            </div>
          </Field>
          <Field label="Working hours / day" hint="Still used for timeline estimates">
            <input
              required
              type="number"
              min="0"
              max="24"
              value={form.working_hours_per_day}
              onChange={(e) => update('working_hours_per_day', e.target.value)}
              className={`${inputClass} w-32`}
              placeholder="8"
            />
          </Field>
        </div>
      )}

      <Field label="Preferred project types">
        <div className="flex flex-wrap gap-2">
          {PROJECT_TYPES.map((type) => {
            const active = form.preferred_projects.includes(type)
            return (
              <button
                type="button"
                key={type}
                onClick={() => toggleProjectType(type)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                  active
                    ? 'bg-brass/15 border-brass text-brass-dark'
                    : 'bg-paper border-paper-line text-ink/60 hover:border-brass/40'
                }`}
              >
                {type}
              </button>
            )
          })}
        </div>
      </Field>

      {error && <p className="text-sm text-rejected bg-rejected-soft rounded-md px-3 py-2">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="px-6 py-2.5 rounded-md bg-brass text-ink font-medium text-sm hover:bg-brass-light transition-colors disabled:opacity-60"
      >
        {submitting ? 'Saving…' : submitLabel}
      </button>
    </form>
  )
}

const inputClass =
  'w-full px-3 py-2.5 rounded-md border border-paper-line bg-paper text-ink text-sm focus:outline-none focus:ring-2 focus:ring-brass/40 focus:border-brass'

function Field({ label, hint, children }) {
  return (
    <label className="block">
      <span className="flex items-baseline justify-between mb-1.5">
        <span className="text-xs font-medium text-ink/70">{label}</span>
        {hint && <span className="text-[11px] text-ink/40">{hint}</span>}
      </span>
      {children}
    </label>
  )
}
