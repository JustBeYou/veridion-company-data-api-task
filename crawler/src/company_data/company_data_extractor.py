"""
Company data extractor module.

This module provides functionality to extract company data from HTML content.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

import lxml.html
import pyap


@dataclass
class CompanyData:
    """Class for storing company data extracted from websites."""

    url: str
    phone: Optional[str] = None
    social_media: List[str] = field(default_factory=list)
    address: Optional[str] = None


class CompanyDataExtractor:
    """Class for extracting company data from website HTML."""

    def __init__(self) -> None:
        """Initialize the company data extractor."""
        self.logger = logging.getLogger(__name__)
        self.extracted_data: Dict[str, CompanyData] = {}
        self.social_media_domains: Set[str] = {
            # Social Networks
            "facebook.com",
            "fb.com",
            "twitter.com",
            "t.co",
            "linkedin.com",
            "li.com",
            "instagram.com",
            "ig.com",
            "youtube.com",
            "youtu.be",
            "pinterest.com",
            "pin.it",
            "tiktok.com",
            "tiktok.com",
            "snapchat.com",
            "snap.com",
            "reddit.com",
            "redd.it",
            "tumblr.com",
            "tmblr.co",
            "medium.com",
            "medium.com",
            "github.com",
            "gh.io",
            # Professional Networks
            "behance.net",
            "be.net",
            "dribbble.com",
            "dribbble.com",
            "flickr.com",
            "flic.kr",
            "vimeo.com",
            "vimeo.com",
            # Messaging & Communication
            "discord.com",
            "discord.gg",
            "telegram.org",
            "t.me",
            "whatsapp.com",
            "wa.me",
            "wechat.com",
            "wechat.com",
            "line.me",
            "line.me",
            # Regional Networks
            "vk.com",
            "vk.com",
            "ok.ru",
            "ok.ru",
            "weibo.com",
            "weibo.com",
            # Q&A & Professional
            "quora.com",
            "qr.ae",
            "stackoverflow.com",
            "stackoverflow.com",
            # Music & Audio
            "soundcloud.com",
            "soundcloud.com",
            "spotify.com",
            "spoti.fi",
            "apple.com/music",
            "music.apple.com",
            "bandcamp.com",
            "bandcamp.com",
            "mixcloud.com",
            "mixcloud.com",
            "last.fm",
            "last.fm",
            # Creative Platforms
            "deviantart.com",
            "deviantart.com",
            "patreon.com",
            "patreon.com",
            "onlyfans.com",
            "onlyfans.com",
            "substack.com",
            "substack.com",
            # New Social Platforms
            "clubhouse.com",
            "clubhouse.com",
            "threads.net",
            "threads.net",
            "mastodon.social",
            "mastodon.social",
            "bluesky.social",
            "bsky.social",
            # Alternative Social
            "truthsocial.com",
            "truthsocial.com",
            "gettr.com",
            "gettr.com",
            "parler.com",
            "parler.com",
            "gab.com",
            "gab.com",
            # Events & Local
            "meetup.com",
            "meetup.com",
            "eventbrite.com",
            "eventbrite.com",
            "yelp.com",
            "yelp.com",
            "tripadvisor.com",
            "tripadvisor.com",
            "foursquare.com",
            "foursquare.com",
            "nextdoor.com",
            "nextdoor.com",
            # Entertainment & Reviews
            "goodreads.com",
            "goodreads.com",
            "letterboxd.com",
            "letterboxd.com",
            # Podcast Platforms
            "anchor.fm",
            "anchor.fm",
            "podbean.com",
            "podbean.com",
            "buzzsprout.com",
            "buzzsprout.com",
            "libsyn.com",
            "libsyn.com",
            "spreaker.com",
            "spreaker.com",
            "acast.com",
            "acast.com",
            "spotify.com/podcasts",
            "open.spotify.com/show",
            "apple.com/podcasts",
            "podcasts.apple.com",
            "google.com/podcasts",
            "podcasts.google.com",
            "stitcher.com",
            "stitcher.com",
            "iheart.com",
            "iheart.com",
            "tunein.com",
            "tunein.com",
            "radiopublic.com",
            "radiopublic.com",
            "overcast.fm",
            "overcast.fm",
            "castbox.fm",
            "castbox.fm",
            "player.fm",
            "player.fm",
            "podchaser.com",
            "podchaser.com",
            "podcastaddict.com",
            "podcastaddict.com",
            "podcastrepublic.com",
            "podcastrepublic.com",
            "podcastindex.org",
            "podcastindex.org",
        }

    def extract(self, url: str, html_content: str) -> CompanyData:
        """
        Extract company data from HTML content.

        Args:
            url: URL of the website
            html_content: HTML content of the website

        Returns:
            CompanyData: Extracted company data
        """
        company_data = CompanyData(url=url)

        try:
            html = lxml.html.fromstring(html_content)

            company_data.phone = self.extract_phone(html)
            company_data.social_media = self.extract_social_media(html)
            company_data.address = self.extract_address(html)

            self.extracted_data[url] = company_data

        except Exception as e:
            self.logger.error(f"Error extracting data from {url}: {str(e)}")

        return company_data

    def extract_phone(self, html: lxml.html.HtmlElement) -> Optional[str]:
        """
        Extract phone number from HTML.

        Args:
            html: Parsed HTML

        Returns:
            Optional[str]: Phone number if found, None otherwise
        """
        # Look for phone patterns in text
        text_elements = html.xpath("//text()")
        text_content = " ".join(str(text) for text in text_elements)

        phone_patterns = [
            r"^(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}$",
            r"\(\d{3}\)\s*\d{3}-\d{4}",  # (555) 123-4567
            r"\d{3}-\d{3}-\d{4}",  # 555-123-4567
            r"\+\d{1,3}\s*\(\d{3}\)\s*\d{3}-\d{4}",  # +1 (555) 123-4567
            r"\+\d{1,3}\s*\d{3}\s*\d{3}\s*\d{4}",  # +1 555 123 4567
        ]

        for pattern in phone_patterns:
            matches = re.findall(pattern, text_content)
            if matches and len(matches) > 0:
                return str(matches[0])

        return None

    def extract_social_media(self, html: lxml.html.HtmlElement) -> List[str]:
        """
        Extract social media links from HTML.

        Args:
            html: Parsed HTML

        Returns:
            List[str]: List of social media links
        """
        social_links: List[str] = []
        link_elements = html.xpath("//a/@href")

        for link in link_elements:
            link_str = str(link)
            if self.is_valid_social_media_url(link_str):
                social_links.append(link_str)

        return social_links

    def extract_address(self, html: lxml.html.HtmlElement) -> Optional[str]:
        """
        Extract address from HTML.

        Args:
            html: Parsed HTML

        Returns:
            Optional[str]: Address if found, None otherwise
        """
        # Look for common address containers
        address_elements = html.xpath('//div[contains(@class, "address")]')
        if address_elements and len(address_elements) > 0:
            text_elements = address_elements[0].xpath(".//text()")
            address = " ".join(str(text) for text in text_elements).strip()
            if address:
                return address

        # # Look for address patterns
        text_elements = html.xpath("//text()")
        text_content = " ".join(str(text) for text in text_elements)

        for country in ["US", "CA"]:
            try:
                addresses = pyap.parse(text_content, country=country)
                if addresses and len(addresses) > 0:
                    return str(addresses[0])
            except Exception as e:
                self.logger.error(f"Error parsing address: {str(e)}")

        return None

    def normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number format.

        Args:
            phone: Phone number to normalize

        Returns:
            str: Normalized phone number (E.164 format)
        """
        # Extract digits only
        return "".join(re.findall(r"\d", phone))

    def is_valid_social_media_url(self, url: str) -> bool:
        """
        Check if a URL is a valid social media link to a profile, page, or channel.

        Args:
            url: URL to check

        Returns:
            bool: True if it's a valid social media profile/page/channel URL, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower().strip("/")

            # Handle cases where domain starts with www.
            if domain.startswith("www."):
                domain = domain[4:]

            # Check if it's a social media domain
            if not any(sm_domain == domain for sm_domain in self.social_media_domains):
                return False

            # Skip empty paths or just root
            if not path:
                return False

            # Define patterns for non-useful pages to exclude
            excluded_patterns = [
                "login",
                "signin",
                "signup",
                "register",
                "auth",
                "oauth",
                "help",
                "support",
                "contact",
                "about",
                "terms",
                "privacy",
                "policy",
                "settings",
                "account",
                "preferences",
                "api",
                "developer",
                "docs",
                "legal",
                "careers",
                "jobs",
                "press",
                "blog",
                "news",
                "faq",
                "search",
                "explore",
                "trending",
                "discover",
                "notifications",
                "messages",
                "inbox",
                "home",
                "feed",
                "timeline",
                "dashboard",
                "ads",
                "advertising",
                "business",
                "create",
                "upload",
                "post",
                "logout",
                "404",
                "error",
                "maintenance",
                "status",
            ]

            # Check if path contains any excluded patterns
            if any(pattern in path for pattern in excluded_patterns):
                return False

            # Domain-specific validation patterns
            domain_patterns = {
                "facebook.com": [
                    r"^[^/]+/?$",  # /username
                    r"^pages?/",  # /pages/...
                    r"^profile\.php",  # /profile.php?id=...
                    r"^groups?/",  # /groups/...
                ],
                "fb.com": [r"^[^/]+/?$"],
                "twitter.com": [
                    r"^[^/]+/?$",  # /username
                    r"^[^/]+/status/\d+",  # /username/status/123 (tweets)
                ],
                "t.co": [r"^[a-zA-Z0-9]+/?$"],  # Short links
                "linkedin.com": [
                    r"^in/[^/]+/?$",  # /in/username
                    r"^company/[^/]+/?$",  # /company/name
                    r"^pub/[^/]+",  # /pub/username
                    r"^school/[^/]+/?$",  # /school/name
                ],
                "li.com": [r"^[a-zA-Z0-9-]+/?$"],  # Short links
                "instagram.com": [
                    r"^[^/]+/?$",  # /username
                    r"^p/[a-zA-Z0-9_-]+",  # /p/post_id
                    r"^reel/[a-zA-Z0-9_-]+",  # /reel/reel_id
                ],
                "youtube.com": [
                    r"^c/[^/]+/?$",  # /c/channel
                    r"^channel/[^/]+/?$",  # /channel/id
                    r"^user/[^/]+/?$",  # /user/username
                    r"^@[^/]+/?$",  # /@username
                    r"^watch\?v=[a-zA-Z0-9_-]+",  # /watch?v=video_id
                ],
                "youtu.be": [r"^[a-zA-Z0-9_-]{11}/?$"],  # Short video links
                "github.com": [
                    r"^[^/]+/?$",  # /username or /org
                    r"^[^/]+/[^/]+/?$",  # /username/repo
                ],
                "pinterest.com": [
                    r"^[^/]+/?$",  # /username
                    r"^[^/]+/[^/]+/?$",  # /username/board
                ],
                "tiktok.com": [
                    r"^@[^/]+/?$",  # /@username
                    r"^@[^/]+/video/\d+",  # /@username/video/id
                ],
                "reddit.com": [
                    r"^r/[^/]+/?$",  # /r/subreddit
                    r"^u/[^/]+/?$",  # /u/username
                    r"^user/[^/]+/?$",  # /user/username
                ],
                "medium.com": [
                    r"^@[^/]+/?$",  # /@username
                    r"^[^/]+/?$",  # /publication or /username
                ],
                "behance.net": [r"^[^/]+/?$"],  # /username
                "dribbble.com": [r"^[^/]+/?$"],  # /username
                "vimeo.com": [
                    r"^[^/]+/?$",  # /username
                    r"^\d+/?$",  # /video_id
                ],
                "soundcloud.com": [r"^[^/]+/?$"],  # /username
                "spotify.com": [
                    r"^user/[^/]+/?$",  # /user/username
                    r"^artist/[^/]+/?$",  # /artist/id
                    r"^playlist/[^/]+/?$",  # /playlist/id
                ],
                "twitch.tv": [r"^[^/]+/?$"],  # /username
            }

            # Check domain-specific patterns
            if domain in domain_patterns:
                patterns = domain_patterns[domain]
                return any(re.match(pattern, path) for pattern in patterns)

            # For other social media domains, accept if path looks like a username/profile
            # (single path component, not containing common non-profile patterns)
            path_parts = [part for part in path.split("/") if part]
            if len(path_parts) == 1:
                # Single path component - likely a username/profile
                username = path_parts[0]
                # Check if it looks like a reasonable username (alphanumeric, underscores, hyphens)
                if re.match(r"^[a-zA-Z0-9_.-]+$", username) and len(username) > 0:
                    return True

            return False

        except Exception:
            return False

    def has_data(self, url: str) -> bool:
        """
        Check if data has been extracted for a URL.

        Args:
            url: URL to check

        Returns:
            bool: True if data exists, False otherwise
        """
        return url in self.extracted_data
