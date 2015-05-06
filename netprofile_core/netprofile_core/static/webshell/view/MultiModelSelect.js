/**f
 * @class NetProfile.view.MultiModelSelect
 * @extends Ext.form.field.ComboBox
 */

Ext.define('comboSelectedCount', {
    alias: 'plugin.selectedCount',
    requires: ['NetProfile.view.MultiModelSelect'],
    init: function (combo) {
        var fl = combo.getFieldLabel(),
        allSelected = false,
        id = combo.getId() + '-toolbar-panel';

        Ext.apply(combo, {
            listConfig: {
                tpl : new Ext.XTemplate(
                                    '<div id="' + id + '"></div><tpl for="."><div class="x-boundlist-item">{' + combo.displayField + '}</div></tpl>'
                )
            }
        });
        var toolbar = Ext.create('Ext.toolbar.Toolbar', {
            items: [{
                text: 'Select all',
                handler: function(btn, e) {
                    if( ! allSelected) {
                        combo.select(combo.getStore().getRange());
                        combo.setSelectedCount(combo.getStore().getRange().length);
                        var records = [];
                        var cbvalue = combo.getValue();
                        for (var i=0; i < cbvalue.length; i++) {
                            var cbrecord =  combo.findRecordByValue(cbvalue[i]);
                            records.push(cbrecord);
                        }
                        NetProfile.view.MultiModelSelect.setSelectedRecords(combo, records); 
                        btn.setText('Deselect all...');
                        allSelected = true;
                        //maybe close combo after selecting all?
                    }else{
                        combo.reset();
                        btn.setText('Select all...');
                        allSelected = false;
                    }
                    e.stopEvent();
                }
            }]
        });
        combo.on({select: function (me, records) {
            NetProfile.view.MultiModelSelect.setSelectedRecords(me, records);            
        },
                  beforedeselect: function (me, record, index) {
                      me.setFieldLabel(fl);
                  },
                  expand: {
                      fn: function() {
                          var dropdown = Ext.get(id).dom.parentElement;
                          var container = Ext.DomHelper.insertBefore(dropdown, '<div id="'+id+'-container"></div>', true);
                          toolbar.render(container);
                      },
                      single: true
                  }
                 });
        combo.setSelectedCount = function(count) {
            combo.setFieldLabel(fl + ' (' + count + ' selected)');
        }
    }
});

Ext.define('NetProfile.view.MultiModelSelect', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.multimodelselect',
    statics: {
        setSelectedRecords: function (combo, records) {
            var len = records.length,
            store = combo.getStore();
            combo.setSelectedCount(len);
            if(!combo.hiddenField)
		return;
	    var form = combo.up('form'),
	    hf = form.down('field[name=' + combo.hiddenField + ']');
            if(!hf)
		return;
	    if(records && records.length)
                var uids = [];
            for (var i = 0; i < records.length; i++) {
                uids.push(records[i].getId());
            }
	    hf.setValue(JSON.stringify(uids));
        }
    },
    plugins: [{
        ptype: 'selectedCount'
    }],
    requires: [
    ],
    apiModule: null,
    apiClass: null,
    hiddenField: null,
    extraParams: null,
    
    editable: false,
    multiSelect: true,  
    valueField: '__str__',
    displayField: '__str__',

    initComponent: function()
    {
	if(!this.store)
	{
	    this.store = NetProfile.StoreManager.getStore(
		this.apiModule,
		this.apiClass,
		null, true, true,
		this.extraParams
	    );
	}
	this.callParent(arguments);
    }
});

