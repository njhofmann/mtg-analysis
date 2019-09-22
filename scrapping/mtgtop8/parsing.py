
import datetime
import re

# regex constants
EVENT_URL_REGEX = re.compile('event\?e=[0-9]+&f=[A-Z]+')
EVENT_SIZE_REGEX = re.compile('[0-9]+ players')
DECK_URL_REGEX = re.compile('\?e=[0-9]+&d=[0-9]+&f=[A-Z]+')
DECK_ARCHETYPE_REGEX = re.compile('archetype?\?a=[0-9]+')

# malformed urls
MALFORMED_EVENT_URLS = ['https://www.mtgtop8.com/event?e=7018&f=LE']


def format_date(date):
    """
    Formats a 'dd/mm/yyyy' date into a 'mm/dd/yyyy'.
    :param date: give date to format
    :return: formatted date
    """
    parsed_date = datetime.datetime.strptime(date, '%d/%m/%y')
    return parsed_date.strftime('%m/%d/%Y')


def get_event_size(event):
    possible_texts = event.find_all(class_='S14')
    for text in possible_texts:
        size = EVENT_SIZE_REGEX.search(text.get_text())
        if size:  # is not None
            return int(size.group().split(' ')[0])
    return None


def get_entry_rank(parent_elements):
    rank = parent_elements.find(class_='W14')
    if rank is None:
        rank = parent_elements.find(class_='S14')
    return rank.get_text()


def card_in_mainboard(card):
    """

    :param card:
    :return:
    """
    for prev_sib in card.parent.previous_siblings:
        has_class = prev_sib.find(class_='O13')
        if has_class is not None:
            title = has_class.get_text().lower()
            if 'sideboard' in title:
                return False
    return True


def get_events_from_page(url_soup, url_format, logger):
    """

    :param url_data:
    :param page:
    :param url_format:
    :param logger:
    :return:
    """
    parents = url_soup.find_all(class_='hover_tr')  # combine parent.find() into lambda
    events = [parent for parent in parents if parent.find(href=EVENT_URL_REGEX)]

    # parse out events in last major events column
    normal_events = []
    for parent in events:
        if parent.previous_siblings is None:  # should never occur
            normal_events.append(parent)
        else:
            major_event_header = any(['class="w_title"' in str(sibling)
                                      and 'Last major events' in str(sibling)
                                      for sibling in parent.previous_siblings])
            if not major_event_header:
                normal_events.append(parent)

    # empty pages == final page has been reached
    if len(normal_events) < 1:
        return None

    to_return = [_ for _ in normal_events]
    for idx, event in enumerate(normal_events):
        event_info = event.find(href=EVENT_URL_REGEX)
        event_url_ending = event_info['href']
        if event_url_ending not in MALFORMED_EVENT_URLS:
            event_name = event_info.get_text()
            event_date = format_date(event.find(class_='S10').get_text())
            to_return[idx] = (event_name, event_date, event_url_ending)
    return to_return


def get_event_info(url_soup):
    """

    :param url_soup:
    :return:
    """
    possible_parents = url_soup.find_all(class_=lambda tag: tag in ('chosen_tr', 'hover_tr'))
    deck_parents = [parent for parent in possible_parents if parent.find(href=DECK_URL_REGEX)]
    size = get_event_size(url_soup)
    return deck_parents, size


def get_event_entry_info(entry_soup):
    """

    :param entry_soup:
    :return:
    """
    child_deck_tag = entry_soup.find(href=DECK_URL_REGEX)
    entry_url_ending = 'event' + child_deck_tag['href']
    deck_name = child_deck_tag.get_text()
    deck_rank = get_entry_rank(entry_soup)
    player_name = entry_soup.find(class_='G11').get_text()
    return entry_url_ending, deck_name, deck_rank, player_name


def get_entry_deck_info(entry_soup):
    """

    :param entry_soup:
    :return:
    """
    # attempt to find archetype, if not just give deck name
    deck_archetype = entry_soup.find(href=DECK_ARCHETYPE_REGEX)
    if deck_archetype is not None:
        deck_archetype = deck_archetype.get_text()

    # find all cards apart of the deck
    cards = entry_soup.find_all(class_='G14')
    return cards, deck_archetype


def get_card_info(card_soup):
    """

    :param card_soup:
    :return:
    """
    card_name = card_soup.find(class_='L14').get_text()
    in_mainboard = str(card_in_mainboard(card_soup))  # check in sideboard
    quantity = int(card_soup.find(class_='hover_tr').get_text().split(' ')[0])  # TODO clean up
    return card_name, in_mainboard, quantity