# coding=utf-8


def mask(original_string, result_length=None, number_to_leave_alive=None, number_to_mask=None, masking_character=u'*',
         padding_character=u' ', mask_from_direction='right'):
    if result_length is None:
        result_length = len(original_string)

    if number_to_leave_alive is not None:
        if number_to_mask is not None:
            raise ValueError(u'number_to_leave_alive, number_to_mask 중 하나를 제시해야 함')
    else:
        if number_to_leave_alive is None:
            raise ValueError(u'number_to_leave_alive, number_to_mask 중 하나를 제시해야 함')
        number_to_leave_alive = result_length - number_to_mask

    if mask_from_direction == 'right':
        padded = original_string[:number_to_leave_alive].ljust(number_to_leave_alive, padding_character)
        return padded.ljust(result_length, masking_character)
    elif mask_from_direction == 'left':
        padded = original_string[number_to_leave_alive:].rjust(number_to_leave_alive, padding_character)
        return padded.rjust(result_length, masking_character)
    else:
        raise ValueError(u"mask_from_direction: 'left', 'right' 중 하나여야 함")