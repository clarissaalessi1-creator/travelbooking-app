# Assignment 2 Part 1 — Geo Hotel Map Research

**Status:** Research and early design only. Geoapify integration and Leaflet map
rendering have not been implemented. Existing Assignment 1 search, bookings,
SQLite data, and instructor CSV values remain unchanged.

## Proposed request sequence

The browser should call a local FastAPI endpoint, never Geoapify directly. The
backend will read `GEOAPIFY_API_KEY` from its environment, make the two upstream
requests, and return a narrowed JSON shape to Vue. `.env` is already ignored by
Git. This protects the key from browser source and keeps upstream error handling
in one place.

1. Validate and normalize one five-digit U.S. ZIP code (for example, `02108`).
2. Forward-geocode it with a U.S. country filter and a postcode result type:

   ```text
   GET https://api.geoapify.com/v1/geocode/search
       ?text=02108
       &filter=countrycode:us
       &type=postcode
       &limit=5
       &format=json
       &apiKey=GEOAPIFY_API_KEY
   ```

3. Select only a response verified as the requested U.S. ZIP, then find hotels
   within five kilometres of its returned point:

   ```text
   GET https://api.geoapify.com/v2/places
       ?categories=accommodation.hotel
       &filter=circle:{longitude},{latitude},5000
       &bias=proximity:{longitude},{latitude}
       &limit=20
       &apiKey=GEOAPIFY_API_KEY
   ```

Geoapify documents `type=postcode`, `filter=countrycode:us`, response formats,
and the forward-geocoding `lat`/`lon` fields. Its Places API documents
`accommodation.hotel`, circle filters in `lon,lat,radiusMeters` order, and
proximity bias. [Forward geocoding](https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/)
and [Places API](https://apidocs.geoapify.com/docs/places/).

## U.S. ZIP validation and geocoding verification

### Input validation

The first implementation should accept exactly five ASCII digits (`^\\d{5}$`).
This makes the feature's geographic rule clear and avoids silently treating a
ZIP+4 code as a different search area. A non-matching value is an **invalid ZIP**
state and must not call Geoapify. ZIP+4 support is a later, explicit product
decision.

### Resolution rule

A response is a successful resolution only when one result has all of the
following:

- `country_code` is `us` after case normalization;
- `postcode` exactly equals the normalized five-digit input;
- `result_type` is `postcode`;
- `lat` and `lon` are present, numeric, finite, and within geographic ranges.

Use the returned `lat`/`lon` as the search centre, not a city name inferred by
the application. Results that have a U.S. country code but a different postcode
are not a match. An empty collection, or a collection with no verified match,
is the distinct **unresolved ZIP** state. The Geoapify response field reference
lists `postcode`, `country_code`, `result_type`, `lat`, `lon`, and formatted
address fields. [Geoapify Geocoding API](https://apidocs.geoapify.com/docs/geocoding/).

## Places response contract and missing fields

Geoapify Places returns a GeoJSON FeatureCollection. The implementation should
keep no more than the first 20 features for the initial assignment scope and
convert each valid feature to a local `place` object:

| Local field | Preferred Geoapify field | Missing-field rule |
| --- | --- | --- |
| `place_id` | `properties.place_id` | Exclude from interactive results when absent; a stable ID is required to synchronize list and marker selection. |
| `name` | `properties.name` | Omit it when absent. The view must state `Hotel name unavailable from provider.` rather than repurposing an address as a name. |
| `address` | `properties.formatted` | Fall back to joined non-empty `address_line1`, `address_line2`, city, state, and postcode; otherwise show `Address unavailable`. |
| `latitude`, `longitude` | `geometry.coordinates` (`[longitude, latitude]`) | Exclude from the list/map collection when either is missing, non-numeric, or out of range. |
| `categories` | `properties.categories` | Preserve as an optional array; do not derive availability or rating from it. |
| `city`, `state`, `postcode` | corresponding `properties` fields | Optional display metadata only. |

`formatted`, address components, location coordinates, country fields, and
result type are documented geocoding response fields; Places uses category and
location filtering and returns GeoJSON features. [Geocoding response fields](https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/)
and [Places endpoint reference](https://apidocs.geoapify.com/docs/places/).

## Errors, limits, and safe usage

| Condition | Intended local behavior |
| --- | --- |
| ZIP fails local format validation | Show **Invalid ZIP**; make no upstream request. |
| No verified geocoding result | Show **We could not resolve that U.S. ZIP code**; do not call Places. |
| Places returns an empty FeatureCollection | Show **No hotels found within 5 km**; retain the resolved ZIP label. |
| Missing/invalid API key or upstream `401`/`403` | Return a safe configuration/service error; never expose the key or raw upstream URL. |
| Upstream `400` | Treat as a controller-side request-mapping defect; return a generic API error to the UI and log only safe diagnostic context. |
| Upstream `429` | Return a clear retry-later error. Future implementation may use a small, bounded retry that honours `Retry-After`; it must not loop. |
| Timeout, unavailable network, or `5xx` | Return an **API error** state, retain no stale results, and permit a user-initiated retry. |

The Places API requires an API key and supports a `limit` from 1 through 500;
the initial design bounds it at 20 to contain cost and UI volume. Geoapify states
that Places calls are credit-priced by results (20 places per credit) and the
free plan currently includes 3,000 credits per day; plan terms can change.
Geoapify's rate-limit guidance identifies `429`, recommends staying below the
plan limit, and says retries should honour `Retry-After`. [Places limits and
pricing](https://apidocs.geoapify.com/docs/places/), [Geoapify rate-limit
guidance](https://www.geoapify.com/how-to-avoid-429-too-many-requests-with-api-rate-limiting/),
and [pricing FAQ](https://www.geoapify.com/pricing/).

## Leaflet design and interaction model

Leaflet `1.9.4` is installed for the future Vue implementation. The map needs:

- a dedicated container with an explicit CSS height;
- an attributed base tile layer; the early design uses OpenStreetMap and keeps
  its required attribution visible;
- one marker for every local place object and a safe popup built from the local
  display fields;
- a single Vue `selectedPlaceId` state. Selecting a list row highlights its
  marker, opens/focuses its popup, and pans only as needed. Selecting a marker
  sets the same state, applies a visible list-row label, and scrolls that row
  into view; and
- map cleanup when the Vue component unmounts, plus clearing/replacing markers
  before every new result set.

Leaflet's quick start requires map CSS, a defined container height, a tile URL,
and attribution. It supports markers and popups; popup strings must not contain
untrusted HTML. [Leaflet quick start](https://leafletjs.com/examples/quick-start/)
and [Leaflet API reference](https://leafletjs.com/reference.html).

## Useful patterns and selected decisions

Hotel/map interfaces commonly show the same results as a list and on a map.
For example, Airbnb research describes concurrent list-result cards and
map-result pins, while a public description of Google Hotel Search describes a
list panel alongside an active map. We will use that familiar relationship but
will not copy visual assets, code, rankings, pricing conventions, or proprietary
layouts. [Airbnb map/list research](https://arxiv.org/abs/2407.00091) and
[Google Hotel Search description](https://assets.publishing.service.gov.uk/media/67bf20f316dc9038974dbba7/Sanjay_Vakil_response.pdf).

The resulting early design chooses a plain, accessible desktop two-column
layout: controls and a concise status line above, list on the left, map on the
right. On narrow screens, the map follows the list so users still have a
complete non-map result view. A selected place is indicated by a text label,
border, marker style, and popup—not color alone.

## Weaknesses, omissions, and resulting decisions

| Limitation or omission | Resulting design decision |
| --- | --- |
| A ZIP-code centroid is not a ZIP boundary and can put a five-kilometre circle outside the ZIP. | Label results as **within 5 km of the ZIP-code location**, not “in this ZIP.” |
| Places data is external, can change, and is not an exhaustive hotel inventory. | Bound the first view to 20 places and say “results returned by Geoapify”; do not claim every nearby hotel is shown. |
| Geoapify Places does not supply this application's stay availability, booking eligibility, or instructor trip IDs. | Keep map results separate from Assignment 1 SQLite search/bookings. No Book button, database write, or join is part of this feature. |
| Map pins alone are not accessible or sufficient on small screens. | Every mapped result also appears in a keyboard-operable list; mobile stacks the list and map. |
| API keys and upstream error bodies could leak through client-side requests or logging. | Use backend-only key access, safe error mapping, no key logging, and no client-side Geoapify calls. |
| The initial scope does not define ZIP+4, pagination, map-pan requery, deduplication policy, or a production tile provider. | Limit this part to five-digit ZIPs, a single 20-result page, a fixed initial map extent, and an attributed OpenStreetMap development basemap until those choices receive approval. |

## Sources consulted

- <https://apidocs.geoapify.com/docs/geocoding/forward-geocoding/>
- <https://apidocs.geoapify.com/docs/geocoding/>
- <https://apidocs.geoapify.com/docs/places/>
- <https://www.geoapify.com/how-to-avoid-429-too-many-requests-with-api-rate-limiting/>
- <https://www.geoapify.com/pricing/>
- <https://leafletjs.com/download.html>
- <https://leafletjs.com/examples/quick-start/>
- <https://leafletjs.com/reference.html>
- <https://arxiv.org/abs/2407.00091>
- <https://assets.publishing.service.gov.uk/media/67bf20f316dc9038974dbba7/Sanjay_Vakil_response.pdf>
