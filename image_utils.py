import numpy as np
from PIL import Image


def normalize_band(band):
    band = band.astype(np.float32)
    band_min = np.min(band)
    band_max = np.max(band)
    if band_max - band_min == 0:
        return np.zeros_like(band, dtype=np.float32)
    return (band - band_min) / (band_max - band_min)


def apply_rgb_composite(image_data, r_idx, g_idx, b_idx):
    r = normalize_band(image_data[r_idx])
    g = normalize_band(image_data[g_idx])
    b = normalize_band(image_data[b_idx])
    rgb = np.stack([r, g, b], axis=-1)
    rgb_uint8 = (rgb * 255).astype(np.uint8)
    return Image.fromarray(rgb_uint8)


def apply_single_band(image_data, band_index):
    band = normalize_band(image_data[band_index])
    gray = (band * 255).astype(np.uint8)
    return Image.fromarray(gray).convert('RGB')


def apply_filter_logic(image_data, band_names, filter_name):
    # Create lowercase band mapping
    band_dict = {name.lower(): i for i, name in enumerate(band_names)}

    # Get common bands safely
    def get_band(name_fallback, default_idx):
        return normalize_band(image_data[band_dict.get(name_fallback.lower(), default_idx)])

    red = get_band("red", 0)
    green = get_band("green", 1)
    blue = get_band("blue", 2)
    nir = get_band("nir", 3) if "nir" in band_dict else None
    swir = get_band("swir", 4) if len(image_data) > 4 else None

    try:
        if filter_name == "Vegetation Highlight":
            if nir is None:
                raise ValueError("NIR band is required.")
            composite = np.stack([nir, red, green], axis=-1)

        elif filter_name == "Natural Color":
            composite = np.stack([red, green, blue], axis=-1)

        elif filter_name == "Urban/Soil":
            swir = swir if swir is not None else red
            composite = np.stack([swir, red, green], axis=-1)

        elif filter_name == "Water Bodies":
            if nir is None:
                raise ValueError("NIR band is required.")
            water = (blue - nir)
            water = np.clip((water * 255), 0, 255).astype(np.uint8)
            return Image.fromarray(water).convert("RGB")

        elif filter_name == "Healthy Vegetation Contrast":
            if nir is None:
                raise ValueError("NIR band is required.")
            contrast = (nir - red)
            contrast = np.clip((contrast * 255), 0, 255).astype(np.uint8)
            return Image.fromarray(contrast).convert("RGB")

        elif filter_name == "NDVI Enhanced":
            if nir is None:
                raise ValueError("NIR band is required.")
            ndvi = (nir - red) / (nir + red + 1e-6)
            ndvi_rgb = np.stack([
                np.clip(ndvi, 0, 1),
                np.clip(ndvi**2, 0, 1),
                np.clip(ndvi**3, 0, 1)
            ], axis=-1)
            ndvi_rgb = (ndvi_rgb * 255).astype(np.uint8)
            return Image.fromarray(ndvi_rgb)

        elif filter_name == "SAVI (Soil-Adjusted Vegetation Index)":
            if nir is None:
                raise ValueError("NIR band is required.")
            savi = ((nir - red) / (nir + red + 0.5)) * 1.5
            savi = np.clip((savi * 255), 0, 255).astype(np.uint8)
            return Image.fromarray(savi).convert("RGB")

        elif filter_name == "EVI (Enhanced Vegetation Index)":
            if nir is None:
                raise ValueError("NIR band is required.")
            evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
            evi = np.clip((evi * 255), 0, 255).astype(np.uint8)
            return Image.fromarray(evi).convert("RGB")

        else:
            raise ValueError("Unknown filter selected.")

        return Image.fromarray((composite * 255).astype(np.uint8))

    except Exception as e:
        raise RuntimeError(f"Failed to apply filter '{filter_name}': {e}")
