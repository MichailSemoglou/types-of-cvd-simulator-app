"""Enumerations for the CVD Simulator application.

This module defines all enumeration types used throughout the application
to ensure type safety and prevent invalid values.
"""

from __future__ import annotations
from enum import Enum


class CVDType(Enum):
    """Types of color vision deficiencies.

    Color vision deficiencies are categorized based on which cone type
    is affected. Each type simulates how images appear to individuals
    with that specific deficiency.

    Attributes:
        PROTAN: Protanopia - missing or defective L-cones (red).
        DEUTAN: Deuteranopia - missing or defective M-cones (green).
        TRITAN: Tritanopia - missing or defective S-cones (blue).
        GRAYSCALE: Achromatopsia - complete color blindness (grayscale).

    Example:
        >>> cvd_type = CVDType.PROTAN
        >>> print(cvd_type.value)
        'protan'
        >>> print(cvd_type.name)
        'PROTAN'
    """

    PROTAN = "protan"
    DEUTAN = "deutan"
    TRITAN = "tritan"
    GRAYSCALE = "bw"


class Algorithm(Enum):
    """Available simulation algorithms for CVD simulation.

    Each algorithm uses a different scientific method to simulate
    color vision deficiencies. The choice of algorithm affects the
    accuracy and performance of the simulation.

    Attributes:
        BRETTEL_1997: Brettel et al. 1997 algorithm - widely used,
            computationally efficient.
        VIENOT_1999: Viénot et al. 1999 algorithm - improved accuracy
            for severe deficiencies.
        MACHADO_2009: Machado et al. 2009 algorithm - handles severity
            levels well, modern approach.
        VISCHECK: Vischeck algorithm - based on the popular Vischeck tool.
        AUTO: Auto-select algorithm - automatically chooses the best
            algorithm based on deficiency type and severity.

    Example:
        >>> algorithm = Algorithm.MACHADO_2009
        >>> simulator_class = algorithm.get_simulator_class()
        >>> simulator = simulator_class()  # Create simulator instance

    References:
        - Brettel, H., et al. (1997). Computerized simulation of color
          appearance for dichromats. JOSA A.
        - Viénot, F., et al. (1999). Digital video colourmaps for checking
          the legibility of displays by dichromats. Color Research & Application.
        - Machado, G.M., et al. (2009). A physiologically-based model for
          simulation of color vision deficiency. IEEE TVCG.
    """

    BRETTEL_1997 = "brettel_1997"
    VIENOT_1999 = "vienot_1999"
    MACHADO_2009 = "machado_2009"
    VISCHECK = "vischeck"
    AUTO = "auto"

    def get_simulator_class(self) -> type:
        """Get the daltonlens simulator class for this algorithm.

        Returns:
            The daltonlens simulator class.

        Raises:
            ImportError: If daltonlens is not installed.
        """
        from daltonlens import simulate

        mapping = {
            Algorithm.BRETTEL_1997: simulate.Simulator_Brettel1997,
            Algorithm.VIENOT_1999: simulate.Simulator_Vienot1999,
            Algorithm.MACHADO_2009: simulate.Simulator_Machado2009,
            Algorithm.VISCHECK: simulate.Simulator_Vischeck,
            Algorithm.AUTO: simulate.Simulator_AutoSelect,
        }
        return mapping[self]


class OutputFormat(Enum):
    """Supported output image formats.

    Each format has different characteristics regarding:
    - Compression quality
    - File size
    - Transparency support
    - Browser compatibility

    Attributes:
        JPEG: JPEG format - best for photos, lossy compression.
        PNG: PNG format - lossless, supports transparency.
        WEBP: WebP format - modern, excellent compression.
        TIFF: TIFF format - high quality, large files.
        BMP: BMP format - uncompressed, very large files.

    Example:
        >>> fmt = OutputFormat.PNG
        >>> ext = fmt.value  # 'png'
    """

    JPEG = "jpg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"

    @property
    def pil_format(self) -> str:
        """Get the PIL format name.

        Returns:
            The format string used by PIL/Pillow.
        """
        mapping = {
            OutputFormat.JPEG: "JPEG",
            OutputFormat.PNG: "PNG",
            OutputFormat.WEBP: "WEBP",
            OutputFormat.TIFF: "TIFF",
            OutputFormat.BMP: "BMP",
        }
        return mapping[self]


class LogLevel(Enum):
    """Logging levels for the application.

    These correspond to Python's standard logging levels
    but provide type safety within the application.

    Attributes:
        DEBUG: Detailed debugging information.
        INFO: General informational messages.
        WARNING: Warning messages for potential issues.
        ERROR: Error messages for actual errors.
        CRITICAL: Critical errors that may halt the application.
    """

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
