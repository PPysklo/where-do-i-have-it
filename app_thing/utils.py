import numpy as np
import cv2 as cv

from sklearn.cluster import DBSCAN
from PIL import Image as Img
from PIL.Image import Image
from typing import Tuple, Optional

from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol

from django.db.models import Q

from .models import Thing, Location


def search_thing(search_query: str, user_things: Optional[Thing] = None) -> Tuple[Thing, str]:
    """
    Search for things based on the search query.

    Args:
        search_query (str): The search query.
        user_things (Optional[Thing]): The user's things to search within.

    Returns:
        Tuple[Thing, str]: The found things and the search query.
    """
    location = Location.objects.filter(name__icontains=search_query)

    if user_things is not None:
        thing = user_things.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__in=location)
        )
    else:
        thing = Thing.objects.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__in=location)
        )

    return thing, search_query


def image_recognition(img2: Image, img1: Image) -> Tuple[Image, int]:
    """
    Perform image recognition using SIFT and DBSCAN clustering.

    Args:
        img2 (Img): The second image.
        img1 (Img): The first image.

    Returns:
        Tuple[Img, int]: The image with the largest cluster points highlighted and the number of good matches.
    """
    gray_img2 = cv.cvtColor(np.array(img2), cv.COLOR_RGB2GRAY)
    img1 = cv.cvtColor(np.array(img1), cv.COLOR_RGB2GRAY)

    # Initiate SIFT detector
    sift = cv.SIFT_create()

    # Find the key-points and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1, None)
    kp2, des2 = sift.detectAndCompute(gray_img2, None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)  # or pass empty dictionary
    flann = cv.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    # # Need to draw only good matches, so create a mask
    # matchesMask = [[0, 0] for i in range(len(matches))]

    # Ratio test as per Lowe's paper
    good_matches = []
    for m, n in matches:
        if m.distance < 0.8 * n.distance:
            good_matches.append(m)

    if len(good_matches) > 50:
        # Extract matched key-points
        matched_points = np.float32([kp2[m.trainIdx].pt for m in good_matches])

        # Applying DBSCAN clustering to find the largest cluster
        epsilon = 80  # Neighborhood radius
        min_samples = 10  # Minimum number of points in the cluster
        dbscan = DBSCAN(eps=epsilon, min_samples=min_samples)
        clusters = dbscan.fit_predict(matched_points)

        try:
            # Removing noise points
            largest_cluster_label = np.argmax(np.bincount(clusters[clusters != -1]))
            # Selecting points from the largest cluster
            largest_cluster_points = matched_points[clusters == largest_cluster_label]

            # Calculating the coordinates of the rectangle surrounding the points from the largest cluster
            min_x = np.min(largest_cluster_points[:, 0])
            max_x = np.max(largest_cluster_points[:, 0])
            min_y = np.min(largest_cluster_points[:, 1])
            max_y = np.max(largest_cluster_points[:, 1])

        except:
            min_x, min_y, max_x, max_y = 0, 0, 0, 0

        # Draw rectangle around the largest cluster points on the original image
        img2_with_rect = cv.rectangle(np.array(img2),
                                      (int(min_x), int(min_y)),
                                      (int(max_x), int(max_y)),
                                      (255, 0, 0),
                                      4)

        img2 = Img.fromarray(img2_with_rect)

    return img2, len(good_matches)


def qr_decoder(image: Image) -> Optional[Tuple[Image, str, str]]:
    """
    Decode QR codes from an image.

    Args:
        image (Img): The image containing QR codes.

    Returns:
        Optional[Tuple[Img, str, str]]: The cropped image, barcode type, and barcode data if a QR code is found.
    """
    image = np.array(image)

    gray_img = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    barcode = decode(gray_img, symbols=[ZBarSymbol.QRCODE])

    for obj in barcode:
        points = obj.polygon
        (x, y, w, h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))
        
        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type
        
        if barcodeType == "QRCODE":
            img3 = image[y: (y + h + 10), x: (x + w + 10)]
        else:
            img3 = image

        return Img.fromarray(img3), barcodeType, barcodeData


def barcode_decoder(image: Image) -> Optional[Tuple[Image, str, str]]:
    """
    Decode barcodes from an image.

    Args:
        image (Img): The image containing barcodes.

    Returns:
        Optional[Tuple[Img, str, str]]: The image, barcode type, and barcode data if a barcode is found.
    """
    image = np.array(image)

    gray_img = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    barcode = decode(gray_img, symbols=[ZBarSymbol.EAN13])

    for obj in barcode:
        points = obj.polygon
        # (x, y, w, h) = obj.rect
        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        barcodeData = obj.data.decode("utf-8")
        barcodeType = obj.type

        img3 = image

        return Img.fromarray(img3), barcodeType, barcodeData
