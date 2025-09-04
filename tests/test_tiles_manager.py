from mangahub.services import ContentAwareTileManager
from mangahub.core.models.images import ImageMetadata, StripInfo


def test_uniform_strips():
    tm = ContentAwareTileManager()
    strips = tm.generate_strips(
        ImageMetadata(
            url="https://something.com",
            width=800,
            height=1000,
        )
    )

    assert strips == [
        StripInfo(
            image_name="",
            index=0,
            y_start=0,
            y_end=256,
            width=800,
            height=256,
            is_panel_boundary=True,
        ),
        StripInfo(
            image_name="",
            index=1,
            y_start=256,
            y_end=512,
            width=800,
            height=256,
            is_panel_boundary=False,
        ),
        StripInfo(
            image_name="",
            index=2,
            y_start=512,
            y_end=768,
            width=800,
            height=256,
            is_panel_boundary=False,
        ),
        StripInfo(
            image_name="",
            index=3,
            y_start=768,
            y_end=1000,
            width=800,
            height=232,
            is_panel_boundary=True,
        ),
    ]

def test_content_aware_strips():