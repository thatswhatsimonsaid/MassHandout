import re
from enum import StrEnum


class LiturgyOfTheWordSectionEnglish(StrEnum):
    NONE = ""  # Fallback
    FIRST_READING = "READING 1"
    RESPONSORIAL_PSALM = "RESPONSORIAL PSALM"
    SECOND_READING = "READING 2"
    GOSPEL_ACCLAMATION = "GOSPEL ACCLAMATION"
    GOSPEL = "GOSPEL"

    @staticmethod
    def _camelcase_to_snakecase(text: str) -> str:
        # Insert underscore between a lowercase/digit and an uppercase letter
        text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
        # Insert underscore between consecutive uppercase letters followed by lowercase
        text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", text)
        return text.lower()

    @staticmethod
    def to_liturgy_of_the_word_section(lit_word_section: str):
        lit_word_section_snakecase = LiturgyOfTheWordSectionEnglish._camelcase_to_snakecase(lit_word_section)
        match lit_word_section_snakecase:
            case "first_reading":
                return LiturgyOfTheWordSectionEnglish.FIRST_READING
            case "psalm":
                return LiturgyOfTheWordSectionEnglish.RESPONSORIAL_PSALM
            case "second_reading":
                return LiturgyOfTheWordSectionEnglish.SECOND_READING
            case "gospel_acclamation":
                return LiturgyOfTheWordSectionEnglish.GOSPEL_ACCLAMATION
            case "gospel":
                return LiturgyOfTheWordSectionEnglish.GOSPEL
            case _:
                return LiturgyOfTheWordSectionEnglish.NONE


class LiturgyOfTheWordSectionVietnamese(StrEnum):
    NONE = ""  # Fallback
    FIRST_READING = "BÀI ĐỌC I"
    RESPONSORIAL_PSALM = "ĐÁP CA"
    SECOND_READING = "BÀI ĐỌC II"
    GOSPEL_ACCLAMATION = "TUNG HÔ TIN MỪNG"
    GOSPEL = "TIN MỪNG"

    @staticmethod
    def to_liturgy_of_the_word_section(lit_word_section: str):
        lit_word_section_snakecase = LiturgyOfTheWordSectionEnglish._camelcase_to_snakecase(lit_word_section)
        match lit_word_section_snakecase:
            case "first_reading":
                return LiturgyOfTheWordSectionVietnamese.FIRST_READING
            case "psalm":
                return LiturgyOfTheWordSectionVietnamese.RESPONSORIAL_PSALM
            case "second_reading":
                return LiturgyOfTheWordSectionVietnamese.SECOND_READING
            case "gospel_acclamation":
                return LiturgyOfTheWordSectionVietnamese.GOSPEL_ACCLAMATION
            case "gospel":
                return LiturgyOfTheWordSectionVietnamese.GOSPEL
            case _:
                return LiturgyOfTheWordSectionVietnamese.NONE
