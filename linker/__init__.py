"""Reference entity linker for the recipes KG.

This is the bundled REFERENCE implementation. Learners do not modify this
package. To run the integration pipeline against your own lab linker
instead, set USE_MY_LINKER=1 and drop your lab linker into linker_my/.
"""

from linker.link import link
from linker.types import LinkResult

__all__ = ["link", "LinkResult"]
