if (typeof String.prototype.startsWith != 'function') {
	String.prototype.startsWith = function (str) {
		return this.slice(0, str.length) == str;
	};
}

if (typeof String.prototype.endsWith != 'function') {
	String.prototype.endsWith = function (str) {
		return this.slice(-str.length) == str;
	};
}

function handleActionDrop(event, ui) {
	log.debug('handleActionDrop()');
	var column = $(this).attr('data-column');
	var row = $(this).attr('data-row');
	var oldCol = ui.draggable.attr('data-column');
	var oldRow = ui.draggable.attr('data-row');
	var slug = ui.draggable.attr('data-slug');
	var pk = ui.draggable.attr('data-pk');
	var type = ui.draggable.attr('data-type');
	var unlock = ui.draggable.attr('data-unlock');
	var title = ui.draggable.children('a').attr('title');
	var cls = ui.draggable.attr('class');
	var classes = cls.split(" ");
	var fromPalette = false;
	var fromGrid = false;
	for (var i = 0; i < classes.length; i++) {
		if (classes[i] == 'palette-draggable') {
			fromPalette = true;
		}
		if (classes[i].startsWith('sgg-') && classes[i].endsWith('-cell')) {
			fromGrid = true;
		}
	}
//	log.debug('fromPalette=' + fromPalette + ' fromGrid=' + fromGrid);
	if (unlock) {
		unlock = trim1(unlock);
	}
	var levelSlug = findLevelSlug(this);
	var unlockCondition = createUnlockStr(unlock);
	if (fromPalette) {
		ui.draggable.removeClass('palette-draggable');
		ui.draggable.removeClass('ui-draggable-dragging');
		ui.draggable.removeClass('sgg-'+ type + '-palette');
		ui.draggable.addClass('sgg-'+ type + '-cell');
		ui.draggable.addClass('grid_dragable');
		var temp = ui.draggable.clone();
		temp.removeClass('hidden');
		temp.attr('style', '');
		temp.attr('data-column', column);
		temp.attr('data-row', row);
		var html = $('<div />').append(temp).html();
//		log.debug(html);
		$(this).html(html);
//		ui.draggable.addClass('hidden');
		movePaletteAction(slug, levelSlug, column, row);
	} else if (fromGrid) {
		var temp = ui.draggable.clone();
		temp.removeClass('hidden');
		temp.attr('style', '');
		temp.attr('data-column', column);
		temp.attr('data-row', row);
		var html = $('<div />').append(temp).html();
//		log.debug(html);
		$(this).html(html);
//		ui.draggable.addClass('hidden');
		moveGridAction(slug, levelSlug, oldCol, oldRow, column, row);		
	} else if (type == "filler") {
		numFiller += 1;
		slug = 'filler-' + numFiller;
		var text = 'Filler-' + numFiller;
		var drop = createActionDropDiv(slug, type, row, column, text, "-1", text);
		var html = $('<div />').append(drop.clone()).html();
//		log.debug(html);
		$(this).html(html);
		pk = instantiateGridAction(slug, levelSlug, column, row);		
	} else  {
		// From the library
		var drop = createActionDropDiv(slug, type, row, column, ui.draggable.text(), pk, title);
		var html = $('<div />').append(drop.clone()).html();
//		log.debug(html);
		$(this).html(html);
		pk = instantiateGridAction(slug, levelSlug, column, row);		
		if (type == 'event') {
			log.debug('set event date');
	        var modalElement = $('#eventDateChooser');
			var text = "Select the date and time for " + title;
			modalElement.find('#eventName').html(text);
			modalElement.find('input#id_event_slug').val(slug);
	        
	        modalElement.modal({
	            backdrop: true,
	            keyboard: true,
	            show: false
	        }); 
	        modalElement.css('margin-top', (modalElement.outerHeight() / 2) * -1);
	        modalElement.modal('show');		
			
		}
	}
	$(this).children().draggable({
		cursor : 'move',
		start: handleGridStartDrag,
		helper : 'clone',
	});		
}

function handleColumnDrop(event, ui) {
	log.debug('handleColumnDrop()');
	var levelID = findLevelID(this);
	var column = $(this).attr('data-column');
	var slug = ui.draggable.attr('data-slug');
	var pk = ui.draggable.attr('data-pk');
	var levelSlug = findLevelSlug(this);
	if (pk == "-1") {
		$(this).html('');
		deactivateColumn(levelID, column);
	}
	else {
		var drop = createColumnDropDiv(slug, column, ui.draggable.text(), trim2(pk));
		var html = $('<div />').append(drop.clone()).html();
		$(this).html(html);
		activateColumn(levelID, column, slug);
	}
	instantiateGridColumn(slug, levelSlug, column);
}

function handleColumnStartDrag(event, ui) {
	log.debug('handleColumnStartDrag(' + event + ', ' + ui + ')');
	$(this).addClass('hidden');
}

function handleGridStartDrag(event, ui) {
	log.debug('handleGridStartDrag(' + event + ', ' + ui + ')');
	$(this).addClass('hidden');
}

function handleLibraryStartDrag(event, ui) {
	log.debug('handleLibraryStartDrag(' + event + ', ' + ui + ')');
	$(this).addClass('hidden');
}

function handlePaletteStartDrag(event, ui) {
	log.debug('handlePaletteStartDrag(' + event + ', ' + ui + ')');
	$(this).addClass('hidden');
}

function handlePaletteDrop(obj) {
	log.debug('handlePaletteDrop');
	var slug = obj.attr('data-slug');
	var pk = obj.attr('data-pk');
	var type = obj.attr('data-type');
	var title = obj.children('a').attr('title');
	var text = obj.text();
	if (text) {
		text = trim2(text);
	}
//	log.debug("slug = " + slug);
	clearLevelColumnPriority(slug);
	var drop = createPaletteDropDiv(slug, type, text, pk, title);
//	log.debug(drop.html());
	$('.sgg-right-palette').append(drop);
	drop.draggable({
		cursor : 'move',
		start: handlePaletteStartDrag,
		helper : 'clone',
	});
	var slot = obj.parent();
//	log.debug(slot);
	slot.html("");
}

/**
 * Returns a jQuery object that represents the dropped ColumnName.
 * @param slug a String the ColumnName's slug.
 * @param column an int the column the ColumnName is dropped into.
 * @param text a String the name of the column.
 * @returns a jQuery object representing the dropped ColumnName. It can be added to the page.
 */
function createColumnDropDiv(slug, column, text, id) {
	log.debug("createColumnDropDiv(" + slug + ", " + column + ", " + text + ", " + id + ")");
	var drop = $('<div data-slug=' + trim1(slug) + ' class="sgg-column grid-draggable" ' +
			'data-priority=' + column + '><br />' + '<a class="sgg-column-link" ' +
			'href="/challenge_admin/smartgrid/columnname/' + id + '/">'
			+ trim2(text) + '</a><br /></div>');
	return drop;
} 

function instantiateGridColumn(colSlug, levelSlug, column) {
	log.debug('instantiateGridColumn(' + colSlug + ', ' + levelSlug + ', ' + column + ')');
    jQuery.ajax({
        url: "/smartgrid_design/newcol/" + colSlug + "/" + levelSlug + "/" + column + "/", 
        success: function(data) {
//        	log.debug('pk of Grid ColumnName is ' + data.pk);
        	var div = $('div[data-slug="' + catSlug + '"]:visible > a');
        	var href = div.attr('href');
        	href = href.slice(0, href.length - 1);
        	var index = href.lastIndexOf('/');
        	if (index != -1) {
        		href = href.slice(0, index + 1) + data.pk + '/';
//        		log.debug(href);
        		div.attr('href', href);
//        		log.debug(div);
        	}

        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        }
    });		
}

function instantiateGridAction(actSlug, levelSlug, column, row) {
	log.debug('instantiateGridAction(' + actSlug + ', ' + levelSlug + ', ' + column + ', ' + row + ')');
    jQuery.ajax({
        url: "/smartgrid_design/newaction/" + actSlug + "/" + levelSlug + "/" + column + "/" + row + "/", 
        success: function(data) {
//        	log.debug('pk of new Grid Action is ' + data.pk);
        	var div = $('div[data-slug="' + actSlug + '"]:visible > a');
        	var href = div.attr('href');
        	if (href) {
//        		log.debug('href = ' + href);
        		href = href.slice(0, href.length - 1);
        		var index = href.lastIndexOf('/');
        		if (index != -1) {
        			href = href.slice(0, index + 1) + data.pk + '/';
//        		log.debug(href);
        			div.attr('href', href);
//        		log.debug(div);
        		}
        	}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        }
    });		
}

function moveGridAction(actSlug, levelSlug, oldColumn, oldRow, column, row) {
	log.debug('moveGridAction(' + actSlug + ', ' + levelSlug + ', ' + oldColumn + ', ' + oldRow + ', ' + column + ', ' + row + ')');
    jQuery.ajax({
        url: "/smartgrid_design/moveaction/" + actSlug + "/" + levelSlug + "/" + oldColumn + "/" + oldRow + "/" + column + "/" + row + "/", 
        success: function(data) {
//        	log.debug('pk of new Grid Action is ' + data.pk);
        	var div = $('div[data-slug="' + actSlug + '"]:visible > a');
        	var href = div.attr('href');
        	if (href) {
//        		log.debug('href = ' + href);
        		href = href.slice(0, href.length - 1);
        		var index = href.lastIndexOf('/');
        		if (index != -1) {
        			href = href.slice(0, index + 1) + data.pk + '/';
//        		log.debug(href);
        			div.attr('href', href);
//        		log.debug(div);
        		}
        	}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        }
    });		
	
}

function movePaletteAction(actSlug, levelSlug, column, row) {
	log.debug('movePaletteAction(' + actSlug + ', ' + levelSlug + ', ' + column + ', ' + row + ')');
    jQuery.ajax({
        url: "/smartgrid_design/paletteaction/" + actSlug + "/" + levelSlug + "/" + column + "/" + row + "/", 
        success: function(data) {
//        	log.debug('pk of new Grid Action is ' + data.pk);
        	var div = $('div[data-slug="' + actSlug + '"]:visible > a');
        	var href = div.attr('href');
        	if (href) {
//        		log.debug('href = ' + href);
        		href = href.slice(0, href.length - 1);
        		var index = href.lastIndexOf('/');
        		if (index != -1) {
        			href = href.slice(0, index + 1) + data.pk + '/';
//        		log.debug(href);
        			div.attr('href', href);
//        		log.debug(div);
        		}
        	}
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
//        	log.debug(XMLHttpRequest + ' - ' + textStatus + ' - ' + errorThrown);
        }
    });		
	
}

function getDesignerDiff() {
	log.debug('getDesignerDiff()');
	jQuery.ajax({
		url: "/smartgrid_design/get_diff/",
		success: function(data) {
			var diff = data.diff;
			var numDiff = diff.length;
			var diffDiv = $('.sgg-differences');
			if (numDiff == 0) {
				var noDiff = '<u>Changes:</u>No changes from the Smart Grid.';
				diffDiv.html(noDiff);
			}
			else {
				var html = '<u>Changes:</u>';
				for (var i = 0; i < diff.length; i++) {
					var inner = diff[i];
					html += '<div id="diff-' + (i + 1) + '">';
					html += '<div class="sgg-diff-action">' + inner[0] + '</div>';
					html += '<div class="sgg-diff-fields">';
					for (var j = 0; j < inner[1].length; j++) {
						html += '' + inner[1][j] + ', ';
					}
					html = html.substring(0, html.length - 2);
					html += '</div></div>';
				}				
				diffDiv.html(html);
			}
		}
	})
}

function runDesignerLint() {
	log.debug('runDesignerLint()');
	jQuery.ajax({
		url: "/smartgrid_design/run_lint/",
		success: function(data) {
			var unreachable = data.unreachable;
			var false_unlock = data.false_unlock;
			var trees = data.tree;
			var mismatched = data.mismatched_levels;
			var pub_date = data.pub_date;
			log.debug(pub_date);
			var lintDiv = $('#designer-lint');
			var html = '';
			if (unreachable.length > 0) {
				html += '<ul>';
				for (var i = 0; i < unreachable.length; i++) {
					html += '<li><b>' + unreachable[i] + 
						'</b> is unreachable due to unlock condition dependencies</li>';
				}
				html += '</ul>';
			}
			if (mismatched.length > 0) {
				html += '<ul>';
				for (var i = 0; i < mismatched.length; i++) {
					html += '<li>Warning <b>' + mismatched[i] + 
						'</b> depends on an action in a higher level</li>';
				}
				html += '</ul>';
			}
			if (false_unlock.length > 0) {
				html += '<ul>';
				for (var i = 0; i < false_unlock.length; i++) {
					html += '<li>Warning <b>' + false_unlock[i] + 
						'</b> is locked because it depends on an action with a False unlock condition</li>';
				}
				html += '</ul>';				
			}
			if (pub_date.length > 0) {
				html += '<ul>';
				for (var i = 0; i < pub_date.length; i++) {
					html += '<li>Warning <b>' + pub_date[i] +
						'</b>\'s publication or expiration date are outside the competition</li>';
				}
				html += '</ul>';
			}
			html += 'Unlock Condition Dependency:<div class="sgg-unlock-lint">';
			html += trees;
			html += '</div>';
			lintDiv.html(html);
		}
	})
}

/**
 * Returns a jQuery object that represents the dropped Action.
 * @param slug a String the Action slug.
 * @param type a String the type of Action (Activity, commitment, event, filler)
 * @param row an int, the row the Action is in. This will become its priority.
 * @param column an int, the column the Action is in.
 * @param text a String the name of the Action.
 * @returns a jQuery object representing the dropped Action.
 */
function createActionDropDiv(slug, type, row, column, text, id, title) {
	log.debug("createActionDropDiv(" + slug + ", " + type + ", " + row + ", " + column + ", " + text + ", " + id + ")");
	var drop = $('<div data-slug="' + trim2(slug) + '" class="sgg-action sgg-' + trim2(type) + '-cell grid-draggable" ' +
		   	'data-type="' + trim2(type) + '" data-priority="' + row + '" data-column="' + 
		   	column + '" data-pk="' + trim2(id) + '">' +
		   	'<br/>' +
		   	'<a href="/challenge_setting_admin/smartgrid_design/designer' + trim2(type) + '/' + 
		   	trim2(id) + '/"	class="sgg-action" ref="tooltip" title="' + trim2(title) + '">' +
			trim2(text) + '</a><br/></div>');
	return drop;
}

function createPaletteDropDiv(slug, type, text, id, title) {
	log.debug("createPaletteDropDiv(" + slug + ", " + type + ", " + text + ", " + id + ", " + title + ")");
	var drop = $('<div data-slug="' + trim2(slug) + '" class="sgg-action sgg-'+ trim2(type) + '-palette palette-draggable ui-draggable"' +
			'data-type="' + trim2(type) + '" data-pk="' + id + '"><br>' +
			'<a href="/challenge_setting_admin/smartgrid_designer/designer' + trim2(type) + '/' +
			trim2(id) + '/" class="sgg-action" ref="tooltip" title="' + trim2(title) + '">' +
			trim2(text) + '</a><br/></div>');
	return drop;
}

function activateColumn(levelID, column, slug) {
	log.debug("activateColumn("+ levelID + ", " + column + ", " + slug + ")");
	for ( var i = 1; i < 11; i++) {
		var row = $('#' + levelID + ' .sgg-action-dropzone table tbody tr:nth-child(' + i + ')');
		var tdCell = row.find('td:nth-child(' + column + ')');
		var outerDiv = tdCell.children('div');
		outerDiv.removeClass('disabled');
		// Activate the div for dropping.
		outerDiv.droppable({
			accept : '.sgg-action',
			drop : handleActionDrop
		});
	}		
}

function deactivateColumn(levelID, column) {
	log.debug("deactivateColumn("+ levelID + ", " + column + ")");
	for ( var i = 1; i < 11; i++) {
		var row = $('#' + levelID + ' .sgg-action-dropzone table tbody tr:nth-child(' + i + ')');
		var tdCell = row.find('td:nth-child(' + column + ')');
		var outerDiv = tdCell.children('div');
		var innerDiv = outerDiv.children('div');
		var slug = innerDiv.attr('data-slug');
		if (typeof slug == 'string') {
			deleteGridAction(slug);
			$('.library-draggable[data-slug=' + slug + ']').removeClass('hidden');		
		}
		outerDiv.addClass('disabled');
		outerDiv.html('');
	}		
}

function deleteGridAction(actionSlug) {
	log.debug("deleteGridAction(" + actionSlug + ")");
//	$.get("/smartgrid_design/delete_action/" + actionSlug + "/");	
    jQuery.ajax({
        url: "/smartgrid_design/delete_action/" + actionSlug + "/", 
        success: function(data) {
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        }
    });	
}

function deleteGridColumn(colSlug) {
	log.debug("deleteGridColumn(" + colSlug + ")");
    jQuery.ajax({
        url: "/smartgrid_design/delete_column/" + colSlug + "/", 
        success: function(data) {
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        }
    });	
}

function clearLevelColumnPriority(actionSlug) {
	log.debug("clearLevelColumnPriority(" + actionSlug + ")");
    jQuery.ajax({
        url: "/smartgrid_design/clear_from_grid/" + actionSlug + "/", 
        success: function(data) {
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) {
        }
    });	
	
}

/**
 * Trims the whitespace from front and end of str.
 * @param str the string.
 * @returns The string without any spaces in the begging or end.
 */
function trim1 (str) {
    return str.replace(/^\s\s*/, '').replace(/\s\s*$/, '');
}

function trim2(str) {
	if (typeof str == 'string') {
		str = trim1(str);
		var i = str.indexOf('"');
		if (i == 0) {
			str = str.slice(i + 1, str.length - 1);
		}
	}
	return str;
}

/**
 * Searches up the parent tree till data-level is found.
 * @param ele the child element.
 * @returns The level as a string.
 */
function findLevel(ele) {
	var p = ele.parentNode;
	
	while (p) {
		var level = $(p).attr('data-level');
		if (level) {
			return level;
		}
		p = p.parentNode;
	}
	return false;
}

function findLevelSlug(ele) {
	var p = ele.parentNode;
	
	while (p) {
		var level = $(p).attr('data-levelslug');
		if (level) {
			return level;
		}
		p = p.parentNode;
	}
	return false;
	
}

function findLevelID(ele) {
	var p = ele.parentNode;
	
	while (p) {
		var level = $(p).attr('data-level');
		if (level) {
			return $(p).attr('id');
		}
		p = p.parentNode;
	}
	return false;
}	

function findPkForSlug(slug) {
	var ele = $('div[data-slug=' + slug + ']');
	return ele.attr('data-pk');
}

function isCompoundUnlock(unlock) {
	if (unlock) {
		if (unlock.indexOf(" or ") != -1 || unlock.indexOf(" and ")) {
			return true;
		}
	}
	return false;
}

function isSubmittedAction(unlock) {
	if (unlock) {
		var str = "submitted_action(";
		return unlock.slice(0, str.length) == str;
	}
	return false;
}

function getSlugFromUnlock(unlock) {
	if (unlock == "True") {
		return "T";
	}
	if (unlock == "False") {
		return "F";
	}
	if (isSubmittedAction(unlock)) {
		var slug = unlock.slice(17, -1);
		return slug;
	}
	return "";
}

function isSlugInGrid(slug) {
	var ele = $('.sgg-action-slot div[data-slug=' + slug + ']');
	if (ele.length > 0) {
		return true;
	}
	return false;
}

function createUnlockStr(unlockCondText) {
	var unlockText = "";
	if (unlockCondText == "True") {
		unlockText = "T";
	} else if (unlockCondText == "False") {
		unlockText = "F";
	} else if (isCompoundUnlock(unlockCondText)) {
		var conditions = unlockCondText.split(" ");
		unlockText += "[";
		for (var i = 0; i < conditions.length; i++) {
			if (i % 2 == 0) {
				var unlockSlug = getSlugFromUnlock(conditions[i]);
				var pk = findPkForSlug(unlockSlug);
				if (isSlugInGrid(unlockSlug)) {
					unlockText += "" + pk;						
				} else {
					unlockText += "<del><em>" + pk + "</em></del>";
				}
			} else {
				if (conditions[i] == "or") {
					unlockText += ",";
				} else if (conditions[i] == "and") {
					unlockText += "+";
				}
			}
		}
		unlockText += "]";
	} else if (isSubmittedAction(unlockCondText)) {
		var unlockSlug = getSlugFromUnlock(trim1(unlockCondText));
		var pk = findPkForSlug(unlockSlug);
		if (isSlugInGrid(unlockSlug)) {
			unlockText = "[" + pk + "]";				
		} else {
			unlockText = "[<del><em>" + pk + "</em></del>]"; 
		}
	}
	return unlockText;
}